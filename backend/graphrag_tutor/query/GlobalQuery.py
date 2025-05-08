import asyncio
import pandas as pd
import tiktoken
from graphrag.query.indexer_adapters import (
    # read_indexer_communities,
    read_indexer_entities,
    read_indexer_reports,
)
from graphrag.query.llm.oai.chat_openai import ChatOpenAI
from graphrag.query.llm.oai.typing import OpenaiApiType
from graphrag.query.structured_search.global_search.community_context import (
    GlobalCommunityContext,
)
from graphrag.query.structured_search.global_search.search import GlobalSearch
from .CustomGlobalSearch import CustomGlobalSearch
from .constants import (
    API_KEY,
    LLM_MODEL,
    INPUT_DIR,
    COMMUNITY_TABLE,
    COMMUNITY_REPORT_TABLE,
    ENTITY_TABLE,
    ENTITY_EMBEDDING_TABLE,
    COMMUNITY_LEVEL
)


class GlobalQuery:
    def __init__(self):
        # Initialize LLM and token encoder
        self.llm = ChatOpenAI(
            api_key=API_KEY,
            model=LLM_MODEL,
            api_type=OpenaiApiType.OpenAI,
            max_retries=20,
        )
        self.token_encoder = tiktoken.encoding_for_model(LLM_MODEL)

    def load_data(self):
        """Load all necessary data from parquet files."""
        self.community_df = pd.read_parquet(f"{INPUT_DIR}/{COMMUNITY_TABLE}.parquet")
        self.entity_df = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_TABLE}.parquet")
        self.report_df = pd.read_parquet(f"{INPUT_DIR}/{COMMUNITY_REPORT_TABLE}.parquet")
        self.entity_embedding_df = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_EMBEDDING_TABLE}.parquet")

    def prepare_context_builder(self):
        """Prepare the context builder using reports and entities."""
        reports = read_indexer_reports(self.report_df, self.entity_df, COMMUNITY_LEVEL)
        entities = read_indexer_entities(self.entity_df, self.entity_embedding_df, COMMUNITY_LEVEL)

        self.context_builder = GlobalCommunityContext(
            community_reports=reports,
            entities=entities,
            token_encoder=self.token_encoder,
        )

    def get_search_engine(self):
        """Create and configure the search engine."""
        context_builder_params = {
            "use_community_summary": False,
            "shuffle_data": True,
            "include_community_rank": True,
            "min_community_rank": 0,
            "community_rank_name": "rank",
            "include_community_weight": True,
            "community_weight_name": "occurrence weight",
            "normalize_community_weight": True,
            "max_tokens": 12_000,
            "context_name": "Reports",
        }

        map_llm_params = {
            "max_tokens": 1000,
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
        }

        reduce_llm_params = {
            "max_tokens": 2000,
            "temperature": 0.0,
        }

        return CustomGlobalSearch(
            llm=self.llm,
            context_builder=self.context_builder,
            token_encoder=self.token_encoder,
            max_data_tokens=12_000,
            map_llm_params=map_llm_params,
            reduce_llm_params=reduce_llm_params,
            allow_general_knowledge=False,
            json_mode=True,
            context_builder_params=context_builder_params,
            concurrent_coroutines=32,
            response_type="multiple paragraphs",
        )

    async def aquery(self, question):
        """Run the asynchronous query."""
        search_engine = self.get_search_engine()
        result, output_tokens = await search_engine.asearch(question)
        return result.response, result, output_tokens


if __name__ == "__main__":
    pipeline = GlobalQuery()
    pipeline.load_data()
    pipeline.prepare_context_builder()
    question = "Tóm tắt về quyết định ban hành Quy định về quản trị dữ liệu tại Công ty TM & XNK Viettel"
    answer = asyncio.run(pipeline.aquery(question))
    print(answer)
