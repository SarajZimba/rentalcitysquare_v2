from accounting.models import AccountLedger, AccountSubLedger
from purchase.models import AccountProductTracking

def create_subledgers_after_product_create(product):
    ledger = AccountLedger.objects.get(ledger_name="Inventory Purchases")
    subledgername = f'{product.title} ({product.category.title})'
    total = product.cost_price * product.opening_count
    try:
        sub = AccountSubLedger.objects.get(sub_ledger_name=subledgername, ledger=ledger)
        sub.total_value += total
        sub.save()
    except AccountSubLedger.DoesNotExist:
        AccountSubLedger.objects.create(sub_ledger_name=subledgername, ledger=ledger, total_value=total)
    AccountProductTracking.objects.create(product=product, purchase_rate=product.cost_price, quantity=product.opening_count, remaining_stock=product.opening_count)

from organization.models import Branch
from product.models import BranchStockTracking
def check_opening_for_branch():

    branches = Branch.objects.filter(status=True, is_deleted=False)

    branch_status_list = []
    for branch in branches:
         
        has_stock_entries = BranchStockTracking.objects.filter(branch=branch).exists()

        branch_status_list.append({
            'branch': branch,
            'has_stock_entries': has_stock_entries
        })

    return branch_status_list
    
def calculate_cost(product, multiplier=1):
    from decimal import Decimal

    bom_items = product.bom_items.all()
    if not bom_items.exists():
        return Decimal(product.price) * Decimal(multiplier)

    total_cost = Decimal(0)
    for bom in bom_items:
        component_cost = calculate_cost(bom.component_product, bom.quantity * multiplier)
        total_cost += component_cost
    return total_cost


from collections import defaultdict
from decimal import Decimal
from product.models import ProductBOM

def resolve_bom_components(product, quantity_multiplier=Decimal("1.0")):
    """
    Recursively calculate the total raw components for a product based on BOM.
    Returns a dictionary: {component_product: total_quantity}
    """
    components = defaultdict(Decimal)

    bom_items = ProductBOM.objects.filter(parent_product=product)
    if not bom_items.exists():
        # No BOM — treat as raw material
        components[product] += quantity_multiplier
        return components

    for bom_item in bom_items:
        sub_components = resolve_bom_components(
            bom_item.component_product,
            quantity_multiplier * Decimal(bom_item.quantity)
        )
        for sub_product, sub_qty in sub_components.items():
            components[sub_product] += sub_qty

    return components

from collections import defaultdict
from decimal import Decimal
from product.models import ProductBOM

def get_direct_bom_components(product, multiplier=1):
    """
    Returns a flat dict of direct components only (no recursive breakdown).
    """
    components = defaultdict(Decimal)

    for bom in ProductBOM.objects.select_related("component_product").filter(parent_product=product):
        comp = bom.component_product
        quantity = Decimal(bom.quantity) * Decimal(multiplier)
        components[comp] += quantity

    return components
