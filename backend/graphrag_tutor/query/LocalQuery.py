import asyncio
import pandas as pd
import tiktoken
from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
from graphrag.query.indexer_adapters import (
    read_indexer_covariates,
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag.query.input.loaders.dfs import (
    store_entity_semantic_embeddings,
)
from graphrag.query.llm.oai.chat_openai import ChatOpenAI
from graphrag.query.llm.oai.embedding import OpenAIEmbedding
from graphrag.query.llm.oai.typing import OpenaiApiType
from .CustomLocalSearch import CustomLocalSearch
from graphrag.query.structured_search.local_search.mixed_context import (
    LocalSearchMixedContext,
)
from graphrag.query.structured_search.local_search.search import LocalSearch
from graphrag.vector_stores.lancedb import LanceDBVectorStore
from .constants import (
    API_KEY,
    LLM_MODEL,
    EMBEDDING_MODEL,
    INPUT_DIR,
    LANCEDB_URI,
    COMMUNITY_REPORT_TABLE,
    ENTITY_TABLE,
    ENTITY_EMBEDDING_TABLE,
    RELATIONSHIP_TABLE,
    COVARIATE_TABLE,
    TEXT_UNIT_TABLE,
    COMMUNITY_LEVEL
)
from graphrag.query.question_gen.local_gen import LocalQuestionGen

class LocalQuery:
    def __init__(self):
        # Initialize LLM, token encoder, and text embedder
        self.llm = ChatOpenAI(
            api_key=API_KEY,
            model=LLM_MODEL,
            api_type=OpenaiApiType.OpenAI,
            max_retries=20,
        )
        self.token_encoder = tiktoken.get_encoding("cl100k_base")
        self.text_embedder = OpenAIEmbedding(
            api_key=API_KEY,
            api_base=None,
            api_type=OpenaiApiType.OpenAI,
            model=EMBEDDING_MODEL,
            deployment_name=EMBEDDING_MODEL,
            max_retries=20,
        )

    def get_entities(self):
        entity_df = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_TABLE}.parquet")
        entity_embedding_df = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_EMBEDDING_TABLE}.parquet")
        # print(entity_df.head())
        return read_indexer_entities(entity_df, entity_embedding_df, COMMUNITY_LEVEL), entity_df

    def get_entity_description_embeddings(self, entities):
        description_embedding_store = LanceDBVectorStore(
            collection_name="default-entity-description",
        )
        description_embedding_store.connect(db_uri=LANCEDB_URI)
        return store_entity_semantic_embeddings(
            entities=entities, vectorstore=description_embedding_store
        ), description_embedding_store

    def get_relationships(self):
        relationship_df = pd.read_parquet(f"{INPUT_DIR}/{RELATIONSHIP_TABLE}.parquet")
        # print(relationship_df.head())
        return read_indexer_relationships(relationship_df)

    def get_covariates(self):
        covariate_df = pd.read_parquet(f"{INPUT_DIR}/{COVARIATE_TABLE}.parquet")
        # print(covariate_df.head())
        claims = read_indexer_covariates(covariate_df)
        return {"claims": claims}

    def get_reports(self, entity_df):
        report_df = pd.read_parquet(f"{INPUT_DIR}/{COMMUNITY_REPORT_TABLE}.parquet")
        # print(report_df.head())
        return read_indexer_reports(report_df, entity_df, COMMUNITY_LEVEL)

    def get_text_units(self):
        text_unit_df = pd.read_parquet(f"{INPUT_DIR}/{TEXT_UNIT_TABLE}.parquet")
        # print(text_unit_df.head())
        return read_indexer_text_units(text_unit_df)

    def get_search_engine(self):
        entities, entity_df = self.get_entities()
        entity_description_embeddings, description_embedding_store = self.get_entity_description_embeddings(entities)
        relationships = self.get_relationships()
        covariates = self.get_covariates()
        reports = self.get_reports(entity_df)
        text_units = self.get_text_units()


        context_builder = LocalSearchMixedContext(
            community_reports=reports,
            text_units=text_units,
            entities=entities,
            relationships=relationships,
            covariates=covariates,
            entity_text_embeddings=description_embedding_store,
            embedding_vectorstore_key=EntityVectorStoreKey.ID,
            text_embedder=self.text_embedder,
            token_encoder=self.token_encoder,
        )

        local_context_params = {
            "text_unit_prop": 0.5,
            "community_prop": 0.1,
            "conversation_history_max_turns": 5,
            "conversation_history_user_turns_only": True,
            "top_k_mapped_entities": 10,
            "top_k_relationships": 10,
            "include_entity_rank": True,
            "include_relationship_weight": True,
            "include_community_rank": False,
            "return_candidate_context": False,
            "embedding_vectorstore_key": EntityVectorStoreKey.ID,
            "max_tokens": 12_000,
        }

        llm_params = {
            "max_tokens": 2_000,
            "temperature": 0.0,
        }

        return (CustomLocalSearch(
            llm=self.llm,
            context_builder=context_builder,
            token_encoder=self.token_encoder,
            llm_params=llm_params,
            context_builder_params=local_context_params,
            response_type="multiple paragraphs",
        ),
        LocalQuestionGen(
            llm=self.llm,
            context_builder=context_builder,
            token_encoder=self.token_encoder,
            llm_params=llm_params,
            context_builder_params=local_context_params,
        ))

    async def aquery(self, question):
        search_engine, question_generator = self.get_search_engine()
        result, output_tokens = await search_engine.asearch(question)
        final_response = result.response + "\n"
        if result.response == "Xin lỗi, tôi không có đủ thông tin để trả lời câu hỏi trên.":
            question_history = [question]
            candidate_questions = await question_generator.agenerate(
                question_history=question_history, context_data=None, question_count=5
            )
            if len(candidate_questions.response) > 0:
                final_response += " Dưới đây là một số câu hỏi mà bạn có thể quan tâm: \n"
                for candidate_question in candidate_questions.response:
                    final_response += (candidate_question + "\n")

        return final_response, result, output_tokens

if __name__ == "__main__":
    pipeline = LocalQuery()
    question = "Phạm vi điều chỉnh của quyết định Ban hành Quy định về quản trị dữ liệu tại Công ty TM & XNK Viettel"
    answer = asyncio.run(pipeline.aquery(question))
    print(answer)