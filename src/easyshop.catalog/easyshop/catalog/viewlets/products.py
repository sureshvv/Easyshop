# zope imports
from zope.component import queryUtility

# Zope imports
from ZTUtils import make_query       

# plone imports
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

# Five imports
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# CMFCore imports
from Products.CMFCore.utils import getToolByName

# CMFPlone imports
from Products.CMFPlone import Batch      

# Easyshop imports
from easyshop.core.interfaces import ICategory
from easyshop.core.interfaces import ICategoriesContainer
from easyshop.core.interfaces import ICurrencyManagement
from easyshop.core.interfaces import IFormats
from easyshop.core.interfaces import IImageManagement
from easyshop.core.interfaces import INumberConverter
from easyshop.core.interfaces import IPrices
from easyshop.core.interfaces import IProductManagement
from easyshop.core.interfaces import IPropertyManagement
from easyshop.core.interfaces import IShopManagement

class ProductsViewlet(ViewletBase):
    """
    """
    render = ViewPageTemplateFile('products.pt')

    @memoize
    def getFormatInfo(self):
        """
        """
        # Could be overwritten to provide fixed category views.
        # s. DemmelhuberShop
        return IFormats(self.context).getFormats()

    def getImages(self):
        """
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog.searchResults(
            path = {"query" : "/".join(self.context.getPhysicalPath()),
                    "depth" : 1},
            portal_type = "ESImage",
            sort_on = "getObjPositionInParent",
        )
        
        return brains
        
    def getInfo(self):
        """
        """
        batch = self._getBatch()
        # This optimized for speed, as we need _getBatch here anyway.
        # So there is no need of an extra method call within the page 
        # template to get informations we have here already. Same is true 
        # for format infos, see below

        shop = IShopManagement(self.context).getShop()

        parent_category = self.context.getRefs("parent_category")
        if len(parent_category) > 0:
            parent_url = parent_category[0].absolute_url()
        else:
            parent_url = shop.absolute_url()
            
        batch_infos = {
            "parent_url"       : parent_url,
            "previous_url"     : self._getPreviousUrl(batch),
            "previous"         : batch.previous,
            "next_url"         : self._getNextUrl(batch),
            "next"             : batch.next,
            "last_url"         : self._getLastUrl(batch),
            "navigation_list"  : batch.navlist,
            "number_of_pages"  : batch.numpages,
            "page_number"      : batch.pagenumber,
            "absolute_url"     : self.context.absolute_url(),
            "title"            : self.context.Title()
        }
        
        sorting = self.request.SESSION.get("sorting")

        f = self.getFormatInfo()
        products_per_line = f["products_per_line"]
        
        line = []
        products = []        
        for index, product in enumerate(batch):

            # Price
            cm = ICurrencyManagement(self.context)
            p = IPrices(product)

            # Effective price
            price = p.getPriceForCustomer()                                
            price = cm.priceToString(price, symbol="symbol", position="before", suffix=None)
            
            # Standard price
            standard_price = p.getPriceForCustomer(effective=False)
            standard_price = cm.priceToString(standard_price, symbol="symbol", position="before", suffix=None)
                                    
            # Image
            image = IImageManagement(product).getMainImage()
            if image is not None:
                image = "%s/image_%s" % (image.absolute_url(), f.get("image_size"))
            
            # Text    
            temp = f.get("text")
            if temp == "description":
                text = product.getDescription()
            elif temp == "short_text":
                text = product.getShortText()
            elif temp == "text":
                text = product.getText()
            else:
                text = ""

            # Title
            temp = f.get("title")
            if temp == "title":
                title = product.Title()
            elif temp == "short_title":
                title = product.getShortTitle()

            try:
                chars = int(f.get("chars"))
            except (TypeError, ValueError):
                chars = 0
            
            if (chars != 0) and (len(title) > chars):
                title = title[:chars]
                title += "..."
                    
            # CSS Class
            if (index + 1) % products_per_line == 0:
                klass = "last"
            else:
                klass = "notlast"
                            
            line.append({
                "title"                    : title,
                "text"                     : text,
                "url"                      : product.absolute_url(),
                "image"                    : image,
                "for_sale"                 : product.getForSale(),
                "price"                    : price,
                "standard_price"           : standard_price,
                "class"                    : klass,
            })
            
            if (index + 1) % products_per_line == 0:
                products.append(line)
                line = []
        
        # the rest
        if len(line) > 0:
            products.append(line)
        
        # Return format infos here, because we need it anyway in this method
        # This is for speed reasons. See above.
        
        
        
        return {
            "products"    : products, 
            "batch_info"  : batch_infos,
            "format_info" : f,
            "shopurl"     : shop.absolute_url() 
        }

    def getProperties(self):
        """
        """
        u = queryUtility(INumberConverter)
        cm = ICurrencyManagement(self.context)
                
        selected_properties = {}
        for name, value in self.request.form.items():
            if name.startswith("property"):
                selected_properties[name[42:]] = value

        pm = IPropertyManagement(self.context)
        
        result = []
        for property in pm.getProperties():
            options = []
            for option in property.getOptions():

                # generate value string
                name  = option["name"]
                price = option["price"]

                if price != "":
                    price = u.stringToFloat(price)
                    price = cm.priceToString(price, "long", "after", suffix=None)
                    content = "%s %s" % (name, price)
                else:
                    content = name
                        
                # is option selected?
                selected = name == selected_properties.get(property.getId(), False)
                
                options.append({
                    "content"  : content,
                    "value"    : name,
                    "selected" : selected,
                })            
                
            result.append({
                "id"      : property.getId(),
                "title"   : property.Title(),
                "options" : options,
            })

        return result

    def getShopURL(self):
        """
        """
        return IShopManagement(self.context).getShop().absolute_url()  

    def getBreadCrumbs(self) :
        """
        """
        parents = []
        
        parent = self.context.getRefs("parent_category")
        
        while len(parent) > 0 :
          parent = ICategory(parent[0])
          parents.append({"title"   : parent.Title(),
                          "absolute_url"  : parent.absolute_url()
                         }
                        )                            
          parent = parent.getRefs("parent_category")

        parents.reverse()
        
        return parents
        
    @memoize
    def getTdWidth(self):
        """
        """
        return "%s%%" % (100 / self.getFormatInfo().get("products_per_line"))

    def _getBatch(self):
        """
        """
        # Calculate products per page
        fi = self.getFormatInfo()
        products_per_page = fi.get("lines_per_page") * \
                            fi.get("products_per_line")        

        # Get all products                    
        mtool = getToolByName(self.context, "portal_membership")        
        sorting = self.request.SESSION.get("sorting")
        try:
            sorted_on, sort_order = sorting.split("-")
        except (AttributeError, ValueError):
            sorted_on  = "price"
            sort_order = "desc"
        
        pm = IProductManagement(self.context)
        products = pm.getAllProducts(sorted_on=sorted_on,
                                     sort_order = sort_order)
        
        # Get start page
        b_start  = self.request.get('b_start', 0);

        # Calculate Batch
        return Batch(products, products_per_page, int(b_start), orphan=0);

    def _getLastUrl(self, batch):
        """
        """
        query = make_query(self.request.form, {batch.b_start_str:(batch.numpages-1) * batch.length})
        return "%s?%s" % (self.context.absolute_url(), query)

    def _getNextUrl(self, batch):
        """
        """
        try:
            start_str = batch.next.first
        except AttributeError:
            start_str = None 
            
        query = make_query(self.request.form, {batch.b_start_str:start_str})
        return "%s?%s" % (self.context.absolute_url(), query)

    def _getPreviousUrl(self, batch):
        """
        """
        try:
            start_str = batch.previous.first
        except AttributeError:
            start_str = None 
            
        query = make_query(self.request.form, {batch.b_start_str:start_str})
        return "%s?%s" % (self.context.absolute_url(), query)