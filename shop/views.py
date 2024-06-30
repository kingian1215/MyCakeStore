from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from.models import Cake, Order, Profile
from.forms import OrderForm, ProfileForm
import logging
# Create your views here.

logger = logging.getLogger(__name__)

# 商品頁面
def index(request):
    cakes = Cake.objects.all()
    return render(request, 'shop/index.html', {'cakes': cakes})

# 用戶註冊
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            # user = form.save()
            user = form.save(commit=False)
            user.email = profile_form.cleaned_data.get('email')
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # 讀取表單內容並登錄用戶
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
        profile_form = ProfileForm()
    return render(request, 'shop/register.html', {'form': form, 'profile_form': profile_form})

@login_required
def user_logout(request):
    logout(request) #登出
    return redirect('index')

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        # 驗證表單
        if form.is_valid(): 
            # 認證成功
           username = form.cleaned_data.get('username')
           password = form.cleaned_data.get('password')
           user = authenticate(username=username, password=password)
           if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

# @login_required(login_url='/login/')
# def order(request):
#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             order = form.save(commit=False)
#             order.user = request.user
#             # order.cake = Cake.objects.get(id=cake_id)
#             order.save()
#             # 寄送確認信
#             # subject = '您的訂單已送出'
#             # message = '感謝您購買，我們將盡快為您處理。'
#             # from_email = 'Cakeshop <<EMAIL>>'
#             # to_email = request.user.email
#             # send_mail(subject, message, from_email, [to_email])
#             return redirect('order_confirmation', order_id=order.id)
#     else:
#         form = OrderForm()
#     return render(request,'shop/order.html', {'form': form})


@login_required(login_url='/login/')
def order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = OrderForm()
    return render(request, 'shop/order.html', {'form': form})

@login_required(login_url='/login/')
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request,'shop/order_history.html', {'orders': orders})

# @login_required(login_url='/login/')
# def order_confirmation(request, order_id):
#     try:
#         orders = Order.objects.filter(user=request.user, status='Pending')
#         total_price = sum(order.cake.price * order.quantity for order in orders)
#         if request.method == 'POST':
#             order_form = OrderForm(request.POST)
#             if order_form.is_valid():
#                 new_order = order_form.save(commit=False)
#                 new_order.user = request.user
#                 new_order.status = 'Pending'
#                 new_order.save()
#                 return redirect('order_confirmation', order_id=new_order.id)
#     except ObjectDoesNotExist:
#         logger.error('Order does not exist.')
        
#         return redirect('index')
    
#     order_totals = []
#     for order in orders:
#         order_total = order.cake.price * order.quantity
#         order_totals.append({'order':order, 'order_total':order_total})

#     return render(request,'shop/order_confirmation.html', {
#         'orders': order_totals, 
#         'total_price': total_price, 
#         'order_form': OrderForm(), 
#         'order_id': order_id
#         })

@login_required(login_url='/login/')
def order_confirmation(request, order_id):
    try:
        orders = Order.objects.filter(user=request.user, status='Pending')  # Fetch all pending orders for the user
        total_price = sum(order.cake.price * order.quantity for order in orders)  # Calculate total price
        if request.method == 'POST':
            order_form = OrderForm(request.POST)
            if order_form.is_valid():
                new_order = order_form.save(commit=False)
                new_order.user = request.user
                new_order.status = 'Pending'
                new_order.save()
                return redirect('order_confirmation', order_id=new_order.id)
    except ObjectDoesNotExist:
        logger.error("Order does not exist.")
        return redirect('index')
# Calculate individual order item total prices
    order_totals = []
    for order in orders:
        order_total = order.cake.price * order.quantity
        order_totals.append({
            'order': order,
            'order_total': order_total
        })
    return render(request, 'shop/order_confirmation.html', {
        'orders': order_totals,
        'total_price': total_price,
        'order_form': OrderForm(),
        'order_id': order_id
    })

@login_required(login_url='/login/')
def order_confirm(request, order_id):
    try:
        orders = Order.objects.filter(user=request.user, status='Pending')
        total_price = sum(order.cake.price * order.quantity for order in orders)
        try:
            # Send confirmation email
            send_mail(
                'Order Confirmation',
                f'Thank you for your order, {request.user.username}. You have ordered the following items:\n\n' + '\n'.join([f'{order.quantity} x {order.cake.name}' for order in orders]) + f'\n\nTotal price: ${total_price:.2f}.',
                'your-email@gmail.com',  # Replace with your actual email address
                [request.user.email],
                fail_silently=False,
            )
            orders.update(status='Confirmed')
            return redirect('order_history')
        except Exception as e:
            logger.error(f"Error sending email: {e}")
    except ObjectDoesNotExist:
        logger.error('Order does not exist.')
    return redirect('index')
        
@login_required(login_url='/login/')
def order_increase(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='Pending')
    order.quantity += 1
    order.save()
    return redirect('order_confirmation', order_id=order.id)

@login_required(login_url='/login/')
def order_decrease(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='Pending')
    if order.quantity > 1:
        order.quantity -= 1
        order.save()
    return redirect('order_confirmation', order_id=order.id)

@login_required(login_url='/login/')
def order_delete(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='Pending')
    order.delete()
    return redirect('order_confirmation', order_id=order_id)

@login_required(login_url='/login/')
def add_item_to_order(request, order_id):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.user = request.user
            new_order.status = 'Pending'
            new_order.save()
    return redirect('order_confirmation', order_id=order_id)

# @login_required(login_url='/login/')
# def add_to_order(request, order_id):
#     order = get_object_or_404(Order, id=order_id, user=request.user)

#     if request.method == 'POST':
#         cake_id = request.POST.get('cake')
#         quantity = int(request.POST.get('quantity'))
#         cake = get_object_or_404(Cake, id=cake_id)

#         # 添加蛋糕到订单
#         order_item, created = Order.objects.get_or_create(order=order, cake=cake, defaults={'quantity': quantity})
#         if not created:
#             order_item.quantity += quantity
#             order_item.save()

#         return redirect('order_confirmation', order_id=order_id)

#     return render('order_confirmation', {'order': order})

def news(request):
    return render(request, 'shop/news.html')