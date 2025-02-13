from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Dict, Annotated
from app.database.product_service import get_product_by_name, update_product_stock, check_product_stock
from app.database.order_service import create_order, update_order_status
from app.database.wallet_service import get_wallet, update_balance
from decimal import Decimal

class ProductSearchInput(BaseModel):
    product_name: str = Field(..., description="The name of the product to search for")

class ProductSearchTool(BaseTool):
    name: Annotated[str, Field(description="Tool name")] = "product_search"
    description: Annotated[str, Field(description="Tool description")] = "Search for product information by name"
    args_schema: type[BaseModel] = ProductSearchInput

    def _run(self, product_name: str) -> Optional[Dict]:
        return get_product_by_name(product_name)

class CreateOrderInput(BaseModel):
    user_id: str = Field(..., description="The ID of the user placing the order")
    product_id: int = Field(..., description="The ID of the product being ordered")
    quantity: int = Field(..., description="The quantity of the product being ordered")
    total_amount: float = Field(..., description="The total amount of the order")

class CreateOrderTool(BaseTool):
    name: Annotated[str, Field(description="Tool name")] = "create_order"
    description: Annotated[str, Field(description="Tool description")] = "Create a new order for a product"
    args_schema: type[BaseModel] = CreateOrderInput

    def _run(self, user_id: str, product_id: int, quantity: int, total_amount: float) -> Optional[Dict]:
        # Check if product has enough stock
        if not check_product_stock(product_id, quantity):
            print('product_id: ', product_id)
            print('quantity: ', quantity)
            return {
                "error": "Insufficient stock",
                "message": "Product is out of stock"
            }
        
        # Check wallet balance
        wallet = get_wallet(user_id)
        if not wallet:
            return {
                "error": "Wallet not found",
                "message": "Wallet not found"
            }
        
        if wallet['balance'] < Decimal(str(total_amount)):
            return {
                "error": "Insufficient balance",
                "message": f"Insufficient balance. Current balance: {wallet['balance']:,.0f} VND",
                "balance": wallet['balance']
            }
        
        # Deduct money from wallet
        updated_wallet = update_balance(user_id, Decimal(str(-total_amount)))
        if not updated_wallet:
            return {
                "error": "Payment failed",
                "message": "Cannot process payment"
            }
        
        # Update product stock
        if not update_product_stock(product_id, quantity):
            # Refund money if stock update fails
            update_balance(user_id, Decimal(str(total_amount)))
            return {
                "error": "Stock update failed",
                "message": "Cannot update stock"
            }
        
        # Create order
        order = create_order(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total_amount=Decimal(str(total_amount))
        )
        
        if order:
            return {
                "success": True,
                "order": order,
                "message": f"Order created and payment successful. Remaining balance: {updated_wallet['balance']:,.0f} VND"
            }
        
        # If order creation fails, refund money and revert stock
        update_balance(user_id, Decimal(str(total_amount)))
        update_product_stock(product_id, -quantity)  # Add back to stock
        return {
            "error": "Order creation failed",
            "message": "Cannot create order"
        }

class UpdateOrderStatusInput(BaseModel):
    order_id: int = Field(..., description="The ID of the order to update")
    status: str = Field(..., description="The new status of the order")

class UpdateOrderStatusTool(BaseTool):
    name: Annotated[str, Field(description="Tool name")] = "update_order_status"
    description: Annotated[str, Field(description="Tool description")] = "Update the status of an order"
    args_schema: type[BaseModel] = UpdateOrderStatusInput

    def _run(self, order_id: int, status: str) -> bool:
        return update_order_status(order_id, status) 