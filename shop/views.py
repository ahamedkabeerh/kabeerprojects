import json

from django.http import JsonResponse
from django.shortcuts import render,redirect
from shop.form import CustomUserForm
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout

from instamojo_wrapper import Instamojo
from django.conf import settings
api = Instamojo(api_key=settings.API_KEY , auth_token=settings.AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/')



#from shop import keys
#from django.conf import settings
#MERCHANT_KEY=keys.MK
#from django.views.decorators.csrf import csrf_exempt
#from PayTm import Checksum
# Create your views here.
def home(request):
    products=Product.objects.filter(trending=1)
    return render(request,"shop/index.html",{"products":products})
def cart_page(request):
    if request.user.is_authenticated:
        cart=Cart.objects.filter(user=request.user)
        return render(request,"shop/cart.html",{"cart":cart})
    else:
        messages.error(request, "Login to view Cart")
        return redirect("login")

def remove_cart(request,cid):
    cartitem=Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect("/cart")


def favviewpage(request):
    if request.user.is_authenticated:
        fav=Favourite.objects.filter(user=request.user)
        return render(request,"shop/fav.html",{"fav":fav})
    else:
        messages.error(request, "Login to view Favorite")
        return redirect("login")


def remove_fav(request, fid):
    item = Favourite.objects.get(id=fid)
    item.delete()
    return redirect("/favviewpage")

def fav_page(request):
    if request.headers.get('x-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data=json.load(request)

            product_id=data['pid']
            #print(request.user.id)
            product_status = Product.objects.get(id=product_id)
            if product_status:
                if Favourite.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status': 'Product Already in Favourite'}, status=200)
                else:
                    Favourite.objects.create(user=request.user, product_id=product_id)
                    return JsonResponse({'status': 'Product Added to Favourite'}, status=200)

        else:
            return JsonResponse({'status':'Login to Add Favourite'},status=200)
    else:
        return JsonResponse({'status':'Invalid Access'},status=200)

def add_to_cart(request):
    if request.headers.get('x-requested-with')=='XMLHttpRequest':
        if request.user.is_authenticated:
            data=json.load(request)
            product_qty=data['product_qty']
            product_id=data['pid']
            #print(request.user.id)
            product_status = Product.objects.get(id=product_id)
            if product_status:
                if Cart.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status': 'Product Already in Cart'}, status=200)
                #(< span id="cart" > 0 < /span >)
                else:
                    if product_status.quantity >= product_qty:
                        Cart.objects.create(user=request.user, product_id=product_id, product_qty=product_qty)
                        return JsonResponse({'status': 'Product Added to Cart'}, status=200)
                    else:
                        return JsonResponse({'status': 'Product Stock Not Available'}, status=200)
        else:
            return JsonResponse({'status':'Login to Add Cart'},status=200)

    else:
        return JsonResponse({'status':'Invalid Access'},status=200)


def login_page(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method=='POST':
            name=request.POST.get('username')
            pwd=request.POST.get('password')
            user=authenticate(request,username=name,password=pwd)
            if user is not None:
                login(request,user)
                messages.success(request,"Logged in Successfully")
                return redirect("/")
            else:
                messages.error(request,"Invalid User Name or Password")
                return redirect("/login")
        return render(request,"shop/login.html")

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged out Successfully")
    return redirect("/")

def register(request):
    form = CustomUserForm()
    if request.method=='POST':
        form=CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registration Success You can Login Now...!")
            return redirect('/login')
    return render(request,"shop/register.html",{'form':form})
def collections(request):
    catagory=Catagory.objects.filter(status=0)
    return render(request, "shop/collections.html",{"catagory":catagory})

def collectionsview(request,name):
    if (Catagory.objects.filter(name=name,status=0)):
        products=Product.objects.filter(category__name=name)
        return render(request, "shop/products/index.html", {"products": products,"category_name":name})
    else:
        messages.warning(request,"No Such Catagory Found")
        return redirect('collections')


def search_feature(request):
    # Check if the request is a post request.
    if request.method == 'POST':
        # Retrieve the search query entered by the user
        search_query = request.POST['search_query']
        # Filter your model by the search query
        posts = Product.objects.filter(name__icontains=search_query)
        return render(request, 'search.html', {'query': search_query, 'posts': posts})
    else:
        return render(request, 'search.html', {})



def product_details(request,cname,pname):
    if(Catagory.objects.filter(name=cname,status=0)):
        if(Product.objects.filter(name=pname,status=0)):
            products=Product.objects.filter(name=pname,status=0).first()
            return render(request,"shop/products/product_details.html",{"products":products})
        else:
            messages.error(request, "No Such Product Found")
            return redirect('collections')

    else:
        messages.error(request,"No Such Catagory Found")
        return redirect('collections')
def preview(request):
    if request.user.is_authenticated:
        cart=Cart.objects.all()
        return render(request, "shop/checkout.html",{"cart":cart})
    else:
        messages.warning(request,"Login to add a cart")
        return redirect('login')

def checkout(request):

    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('login')
    if request.method == "POST":
        kart=Cart.objects.all()
        for item in kart:
            items_json =item.product.name
            name = request.POST.get('name', '')
            amount =item.total_cost
            email = request.POST.get('email', '')
            address1 = request.POST.get('address1', '')
            address2 = request.POST.get('address2', '')
            city = request.POST.get('city', '')
            state = request.POST.get('state', '')
            zip_code = request.POST.get('zip_code', '')
            phone = request.POST.get('phone', '')
            Order = Orders(items_json=items_json, name=name, amount=amount, email=email, address1=address1,
                       address2=address2, city=city, state=state, zip_code=zip_code, phone=phone)
            orderproduct = Product.objects.filter(id=item.product_id).first()
            orderproduct.quantity = orderproduct.quantity - item.product_qty
            Cart.objects.filter(user=request.user).delete()
            Order.save()


            response = api.payment_request_create(
                amount=str(amount),
                purpose='Order Process',
                buyer_name='Shop Kart',
                email='info@gmail.com',
                redirect_url='http://http://127.0.0.1:8000/order_success/'
            )
            print(response)
        messages.warning(request,"Your Order has been Placed")
        return redirect('/')
    else:
        return redirect('register')

       #id=Order.order_id
       #oid=str(id)+"shopycart"
        #param_dict = {
            #'MID':keys.MID,
            #'ORDER_ID':oid,
            #'TXN_AMOUNT':str(amount),
            #'CUST_ID':email,
            #'INDUSTRY_TYPE_ID':'Retail',
            #'WEBSITE':'WEBSTAGING',
            #'CHANNEL_ID': 'WEB',
            #'CALLBACK_URL':'http://127.0.0.1:8000/handlerequest/',
        #}
        #param_dict['CHECKSUMHASH']=Checksum.generate_checksum
        #(param_dict,MERCHANT_KEY)
        #return render(request,'paytm.html',{'param_dict':param_dict})
    #return render(request,'checkout.html')






