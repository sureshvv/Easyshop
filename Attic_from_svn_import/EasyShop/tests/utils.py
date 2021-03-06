# zope imports
from zope.component import getMultiAdapter
from zope import event

# Archetypes imports
from Products.Archetypes.event import ObjectInitializedEvent

# EasyShop imports 
from Products.EasyShop.interfaces import ICartManagement
from Products.EasyShop.interfaces import IOrderManagement

class TestSession:
    """
    """    
    def __init__(self, sid):
        """
        """
        self.sid = sid
        
    def getId(self):
        """
        """
        return self.sid
        
def createMember(self, id=None):
    """
    """    
    if id is None:
        id = 'newmember'
    
    self.membership = self.portal_membership
    self.membership.addMember(id, 'secret', ['Member'], [])

def createTestEnvironment(self):
    """
    """
    createMember(self, "newmember")
    
    self.manage_addProduct["EasyShop"].addEasyShop(
        id="myshop", 
        title="MyShop", 
        description="My test shop")

    event.notify(ObjectInitializedEvent(self.myshop))

    self.shop = self.myshop
    self.shop.at_post_create_script()

    # Add shipping and payment price
    self.shop.shippingprices.manage_addProduct["EasyShop"].addShippingPrice(id="default", priceGross=10.0)
    self.shop.shippingprices.default.reindexObject()
    
    self.shop.paymentprices.manage_addProduct["EasyShop"].addPaymentPrice(id="default", priceGross=100.0)
    
    self.shop.setCountries(["Germany"])
    self.shop.products.manage_addProduct["EasyShop"].addProduct(id="product_1", priceGross=22.0)
    self.product_1 = self.shop.products.product_1
    self.product_1.setWeight(10.0)

    # Properties
    color = [
        {"name"  : "Red",   "price" : "-10.0"},
        {"name"  : "Blue",  "price" :   "0.0"},
        {"name"  : "Green", "price" :  "15.0"}
    ]

    # Note this will be overwritten by product's properties
    color_for_groups = [
        {"name"  : "Red",   "price" : "1000.0"},
        {"name"  : "Blue",  "price" : "2000.0"},
        {"name"  : "Green", "price" : "3000.0"}
    ]

    material = [
        {"name"  : "Iron", "price" : "-100.0"},
        {"name"  : "Wood", "price" :    "0.0"},
        {"name"  : "Gold", "price" :  "150.0"}
    ]

    quality = [
        {"name"  : "Low",    "price" : "-1000.0"},
        {"name"  : "Medium", "price" :     "0.0"},
        {"name"  : "High",   "price" :  "1500.0"}
    ]

    size_for_groups = [
        {"name"  : "Small",  "price" : "-11.0"},
        {"name"  : "Medium", "price" :   "1.0"},
        {"name"  : "Large",  "price" :  "22.0"}
    ]

    
    self.product_1.manage_addProduct["EasyShop"].addProductProperty(id="color", title="Color")
    self.product_1.color.setOptions(color)

    self.product_1.manage_addProduct["EasyShop"].addProductProperty(id="material", title="Material")
    self.product_1.material.setOptions(material)

    self.product_1.manage_addProduct["EasyShop"].addProductProperty(id="quality", title="Quality")
    self.product_1.quality.setOptions(quality)
    
    self.shop.products.manage_addProduct["EasyShop"].addProduct(id="product_2", priceGross=19.0)
    self.product_2 = self.shop.products.product_2
    self.product_2.setWeight(20.0)

    # A product without properties
    self.shop.products.manage_addProduct["EasyShop"].addProduct(id="product_42", priceGross=19.0)
    self.product_42 = self.shop.products.product_42
    
    # Groups
    self.shop.groups.manage_addProduct["EasyShop"].addProductGroup(id="group_1")
    self.shop.groups.manage_addProduct["EasyShop"].addProductGroup(id="group_2")
    self.group_1 = self.shop.groups.group_1
    self.group_2 = self.shop.groups.group_2

    # Add properties to groups
    self.group_1.manage_addProduct["EasyShop"].addProductProperty(id="color", title="Color")
    self.group_1.color.setOptions(color_for_groups)    

    self.group_1.manage_addProduct["EasyShop"].addProductProperty(id="size", title="Size")
    self.group_1.size.setOptions(size_for_groups)    
        
    # Assign products to groups
    self.group_1.addReference(self.product_1, "group_product")
    self.group_1.addReference(self.product_2, "group_product")  
    self.group_2.addReference(self.product_1, "group_product")    
    
    # Categories
    self.shop.categories.manage_addProduct["EasyShop"].addCategory(id="category_1")
    self.shop.categories.category_1.manage_addProduct["EasyShop"].addCategory(id="category_11")
    self.shop.categories.category_1.manage_addProduct["EasyShop"].addCategory(id="category_12")
    self.shop.categories.category_1.category_11.manage_addProduct["EasyShop"].addCategory(id="category_111")
    self.shop.categories.manage_addProduct["EasyShop"].addCategory(id="category_2")
    
    self.category_1 = self.shop.categories.category_1
    self.category_2 = self.shop.categories.category_2
        
    # Assign products to categories
    self.category_1.category_11.addReference(self.product_1, "easyshopcategory_easyshopproduct")
    self.category_1.category_11.addReference(self.product_2, "easyshopcategory_easyshopproduct")
    
    # taxes    
    self.shop.taxes.manage_addProduct["EasyShop"].addDefaultTax(id="default", rate=19.0)
    
    self.sid = self.REQUEST.SESSION = TestSession("123")

def createTestOrder(self):
    """
    """
    view = getMultiAdapter((self.shop.products.product_1, self.shop.products.product_1.REQUEST), name="addToCart")
    view.addToCart()

    view = getMultiAdapter((self.shop.products.product_2, self.shop.products.product_2.REQUEST), name="addToCart")
    view.addToCart()

    om = IOrderManagement(self.shop)
    self.order = om.addOrder(notify_=False)

    