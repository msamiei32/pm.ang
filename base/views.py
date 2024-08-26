from django.contrib.auth.models import Group
from django.core import serializers
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, CreateView,TemplateView
from django.contrib.auth.decorators import login_required
from django.db.models import DurationField
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q, Sum, F
from django.db.utils import IntegrityError

from review.utils import send_review_order, send_new_order_message, send_completed_message
from users.models import Profile
from django.core.exceptions import PermissionDenied

import jdatetime
from datetime import timedelta

from .models import *
from .forms import OrderForm
from .utils import split_persian_date, is_member, total_seconds_calculator, to_gregorian, find_longest_work,date_jalali
from django.db.models import Count


# from .enum_types import StatusChoices


@login_required(login_url='/users/login/')
def index(request):
    user = request.user
    tasks = None
    all_department = Order.objects.values('department__name')
    list_departement = []
    order_count = []
    list_machine = []
    sum_hours = []
    all_machine = Order.objects.values('operation__name')
    last = Order.published.all().order_by('-createdAt')[:10]
    logo = Logo.objects.all()
    task = Task.published.filter(order__status='WG')
    orde = Order.published.all()
    s = len(task)
    b = len(orde)
    if s or b == 0:
        return render(request,'index.html')
    else:
        cala = round((s / b) * 100)

    # if (s / b) * 100 == 0:
    #     cala = round((s / b) * 100)
    #     print(cala)
    # if round(((s / b) * 100)) == 0:
    #     print(round(((len(task) / len(orde)) * 100)))
    # cala = round(((len(task) / len(orde)) * 100))
    # if cala > 0:
    #     print(cala)


    for tem in all_machine:
        if tem["operation__name"] not in list_machine and tem["operation__name"] is not None:
            tasks = Task.objects.filter(order__operation__name=tem["operation__name"])
            time_spent = 0
            for task in tasks:
                time_spent += task.get_time_diff
            to_time = seconds_to_time(time_spent)
            if to_time > 10:
                sum_hours.append(to_time)
                list_machine.append(tem["operation__name"])
    for item in all_department:
        if item["department__name"] not in list_departement and item["department__name"] is not None:
            list_departement.append(item["department__name"])

            count = Order.objects.filter(department__name=item["department__name"]).count()
            order_count.append(count)

    if user.is_superuser:
        users = User.objects.filter(is_superuser=False)
        orders = Order.published.all()
        tasks = Task.published.all()
        tasks_done = Task.published.filter(order__status='DN')
        tasks_saved = Task.published.filter(order__status='SV')
        tasks_seen = Task.published.filter(order__status='SE')
        tasks_doing = Task.published.filter(order__status='DG')
        tasks_waiting = Task.published.filter(order__status='WG')
        tasks_sent = Task.published.filter(order__status='ST')
        list_department = ['ali', 'hasan', 'gholam']
        # cala = round(((len(tasks_waiting) / len(orders)) * 100))


    else:
        users = User.objects.filter(is_superuser=False)
        orders = Order.published.filter(user=user)
        tasks_done = Task.published.filter(user=user, order__status='DN')
        tasks_saved = Task.published.filter(user=user, order__status='SV')
        tasks_seen = Task.published.filter(user=user, order__status='SE')
        tasks_doing = Task.published.filter(user=user, order__status='DG')
        tasks_waiting = Task.published.filter(user=user, order__status='WG')
        tasks_sent = Task.published.filter(user=user, order__status='ST')
        # cala = round(((len(tasks_waiting) / len(orders)) * 100))
        # list_department = ['ali','hasan','gholam']


    context = {'users': users, 'orders': orders, 'tasks': tasks,
               'tasks_done': tasks_done,
               'tasks_saved': tasks_saved,
               'tasks_seen': tasks_seen,
               'tasks_doing': tasks_doing,
               'tasks_waiting': tasks_waiting,
               'tasks_sent': tasks_sent, 'list_department': list_departement, 'order_count': order_count,
               'list_machine': list_machine, 'time_spent': sum_hours,'order_last':last,'logo':logo,'cal':cala
               }
    return render(request, 'index.html', context)


class OrdersList(ListView):
    model = Order
    template_name = 'order/list.html'
    paginate_by = 30
    context_object_name = 'orders'

    def get_queryset(self):
        if self.request.user.has_perm('review.view_order_all') or is_member(self.request.user):
            orders = Order.published.all().order_by('-createdAt')
        else:
            orders = Order.published.filter(user=self.request.user, isConfirmed=True).order_by('-createdAt')
        if not self.request.user.is_superuser:
            orders = orders.exclude(status='DN')

        q = self.request.GET.get('q')
        year = self.request.GET.get('year')
        department = self.request.GET.get('department')
        operation = self.request.GET.get('operation')
        status = self.request.GET.getlist('status')
        dt_date = self.request.GET.get('dt_date')
        operators = self.request.GET.getlist('operators')

        if year:
            year = year[1:]
            orders = orders.filter(orderId__startswith=year)

        if q:
            orders = orders.filter(Q(orderId__contains=q))

        if department:
            orders = orders.filter(department_id=department)

        if operation:
            orders = orders.filter(operation_id=operation)

        if status:
            orders = orders.filter(status__in=status)

        if operators:
            orders = orders.filter(task__operators__in=operators)

        if dt_date:
            start_date, due_date = dt_date.split(' تا ')
            start_date = jdatetime.datetime.strptime(start_date, '%Y/%m/%d').togregorian().date()
            due_date = jdatetime.datetime.strptime(due_date, '%Y/%m/%d').togregorian().date()
            orders = orders.filter(Q(createdAt__gte=start_date), Q(createdAt__lte=due_date))
        orders = orders.order_by('-createdAt')
        return orders

    def get_context_data(self, **kwargs):
        contains_building = False
        context = super().get_context_data(**kwargs)
        context['operators'] = User.objects.filter(groups__name='اپراتور فنی')
        context['templatetags'] = contains_building
        context['operations'] = Operation.objects.all()
        context['departments'] = Department.objects.all()
        status_choices = Order.StatusChoices
        context['status_choices'] = status_choices
        return context


class OrdersCompletedList(ListView):
    model = Order
    template_name = 'order/completed_list.html'
    paginate_by = 30
    context_object_name = 'orders'

    def get_queryset(self):
        # if self.request.user.has_perm('review.view_order_all') or is_member(self.request.user):
        #     orders = Order.published.all().order_by('-createdAt')
        # else:
        #     orders = Order.published.filter(user=self.request.user, isConfirmed=True).order_by('-createdAt')
        # if not self.request.user.is_superuser:
        orders = Order.published.filter(status='DN')

        q = self.request.GET.get('q')
        department = self.request.GET.get('department')
        operation = self.request.GET.get('operation')
        status = self.request.GET.getlist('status')
        dt_date = self.request.GET.get('dt_date')
        operators = self.request.GET.getlist('operators')
        if q:
            orders = orders.filter(Q(orderId__contains=q))

        if department:
            orders = orders.filter(department_id=department)

        if operation:
            orders = orders.filter(operation_id=operation)

        if status:
            orders = orders.filter(status__in=status)

        if operators:
            orders = orders.filter(task__operators__in=operators)

        if dt_date:
            start_date, due_date = dt_date.split(' تا ')
            start_date = jdatetime.datetime.strptime(start_date, '%Y/%m/%d').togregorian().date()
            due_date = jdatetime.datetime.strptime(due_date, '%Y/%m/%d').togregorian().date()
            orders = orders.filter(Q(createdAt__gte=start_date), Q(createdAt__lte=due_date))
        orders = orders.order_by('-createdAt')

        return orders

    def get_context_data(self, **kwargs):
        contains_building = False
        context = super().get_context_data(**kwargs)
        context['operators'] = User.objects.filter(groups__name='اپراتور فنی')
        context['templatetags'] = contains_building
        context['operations'] = Operation.objects.all()
        context['departments'] = Department.objects.all()
        status_choices = Order.StatusChoices
        context['status_choices'] = status_choices
        return context


def order_add(request):
    if request.method == 'POST':
        operationId = request.POST.get('operation')
        departmentId = request.POST.get('department')
        subgropuIds = request.POST.getlist('subgroup')
        is_department = request.POST.get("create_department")
        is_machine = request.POST.get("create_machine")
        part_id = request.POST.get('part')
        stuff_id = request.POST.get('stuff')
        priority = request.POST.get('priority')
        part = None
        stuff = None
        if part_id:
            part = Part.objects.get(id=part_id)
        elif stuff_id:
            stuff = Stuff.objects.get(id=stuff_id)

        lastOrder = Order.objects.last()
        code = int(lastOrder.orderId) + 1
        print(code)
        code = f'403{str(code)[3:]}'

        # print(str(jdatetime.datetime.now().year)[1:])
        # if jdatetime.datetime.now() == 1402 and str(code).startswith('401'):

        operation = None
        department = None
        if operationId:
            operation = Operation.objects.get(id=operationId)
        elif departmentId:
            department = Department.objects.get(id=departmentId)

        form = OrderForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.orderId = code
            instance.user = request.user
            if operation:
                instance.operation = operation
                instance.operationName = operation.name
            if department:
                instance.department = department
                instance.departmentName = department.name
            if is_machine:
                instance.is_for_machine = True
            if is_department:
                instance.is_for_department = True
            if part:
                instance.part = part
            if stuff:
                instance.stuff = stuff
            instance.priority = priority
            try:
                instance.save()
            except IntegrityError as e:
                messages.error(request, 'این رکورد در این تاریخ یک بار ثبت شده است')
                return redirect('orders_list')
            instance.isConfirmed = True
            # id of ساخت subgroup is 4
            building_subgroup = Subgroup.objects.get(id=1)

            for subgroupId in subgropuIds:
                subgroup_item = Subgroup.objects.get(id=subgroupId)
                if subgroup_item == building_subgroup:
                    instance.isConfirmed = False
                    instance.status = 'درانتظار تایید مدیریت'
                instance.subGroup.add(subgroup_item)

            send_new_order_message(instance, '09160485041')
            instance.save()
        else:
            messages.error(request, 'اطلاعات به صورت صحیح وارد نشده است')

        messages.success(request, 'درخواست ثبت شد')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        form = OrderForm()

    subgroups = Subgroup.objects.all()
    operations = Operation.objects.all()
    departments = Department.objects.all()  # limit the department by technical in form
    context = {'departments': departments, 'operations': operations, 'subgroups': subgroups, 'form': form}
    return render(request, 'order/add.html', context)


@login_required(login_url='/users/login/')
def order_edit(request, orderId):
    order = Order.published.get(orderId=orderId)
    if request.method == 'POST':
        operationId = request.POST.get('operation')
        departmentId = request.POST.get('department')
        part_id = request.POST.get("part")
        subgropupIds = request.POST.getlist('subgroup')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        status = request.POST.get('status')
        operation = Operation.objects.get(id=operationId)
        department = Department.objects.get(id=departmentId)
        part = None
        if part_id:
            part = Part.objects.get(id=part_id)
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.description = description
            instance.operation = operation
            if part:
                instance.part = part
            instance.operationName = operation.name
            instance.status = status
            instance.department = department
            instance.departmentName = department.name
            instance.priority = priority
            if status == 'DN':
                phone_numbers = PhoneNumber.objects.all()
                # ['09192955815',
                #     '09160485041']
                for phone_number in phone_numbers:
                    send_completed_message(instance, phone_number)
            instance.save()

            instance.subGroup.clear()
            for subgroupId in subgropupIds:
                instance.subGroup.add(Subgroup.objects.get(id=subgroupId))

            instance.save()
        messages.success(request, 'درخواست ویرایش شد')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        form = OrderForm(request.POST or None, instance=order)
    subgroups = Subgroup.objects.all()
    operations = Operation.objects.all()
    departments = Department.objects.filter(id=3)  # limit the department by technical in form
    status_choices = Order.StatusChoices
    context = {'departments': departments, 'operations': operations, 'subgroups': subgroups, 'order': order,
               'form': form, "status_choices": status_choices}
    return render(request, 'order/edit.html', context)


def order_detail(request, orderId):
    order = Order.published.get(orderId=orderId)
    context = {'order': order}
    return render(request, 'order/detail.html', context)


def order_invoice(request, orderId):
    order = Order.published.get(orderId=orderId)
    context = {'order': order}
    return render(request, 'order/invoice.html', context)


class TasksList(ListView):
    model = Task
    template_name = 'task/list.html'
    paginate_by = 10
    context_object_name = 'tasks'

    def get_queryset(self):
        if self.request.user.is_superuser:
            # exclude tasks which their orders are not published
            tasks = Task.published.all().order_by('-date').exclude(order__publish=False)
        else:
            tasks = Task.published.filter(user=self.request.user).order_by('-date').exclude(order__publish=False)

        q = self.request.GET.get('q')
        department = self.request.GET.get('department')
        status = self.request.GET.getlist('status')
        operation = self.request.GET.get('operation')
        subgroup = self.request.GET.get('subgroup')
        operator = self.request.GET.getlist('operator')
        dt_date = self.request.GET.get('dt_date')
        year = self.request.GET.get('year')

        if q:
            tasks = tasks.filter(order__orderId__contains=q)

        if department:
            tasks = tasks.filter(order__department_id=department)

        if status:
            orders = list(Order.objects.filter(task__in=tasks, status__in=status).values_list('id', flat=True))
            tasks = tasks.filter(order_id__in=orders)

        if operation:
            tasks = tasks.filter(order__operation=operation)

        if subgroup:
            tasks = tasks.filter(order__subGroup=subgroup)

        if operator != [''] and operator:
            tasks = tasks.filter(operators__in=operator)

        if dt_date:
            start_date, due_date = dt_date.split(' تا ')
            start_date = jdatetime.datetime.strptime(start_date, '%Y/%m/%d').togregorian().date()
            due_date = jdatetime.datetime.strptime(due_date, '%Y/%m/%d').togregorian().date()
            tasks = tasks.filter(Q(date__gte=start_date), Q(date__lte=due_date))

        tasks = tasks.order_by('-date')
        return tasks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        context['operations'] = Operation.objects.all()
        context['operators'] = User.objects.filter(groups__name='اپراتور فنی')
        status_choices = Order.StatusChoices
        context['status_choices'] = status_choices
        tasks = self.get_queryset()
        time_spent = 0
        for task in tasks:
            time_spent += task.get_time_diff

        context['time_spent'] = time_spent
        return context


def list_task_of_order(request):
    order_id = request.GET.get("order_id")
    task_id = request.GET.get("task_id")
    all_task = Task.objects.filter(order__orderId=order_id).exclude(id=task_id).values(
        'id', 'user', 'description', 'description2', 'date', 'start_time', 'end_time', 'status')
    data = []

    for item in all_task:
        tem = {}
        m_user = User.objects.get(id=item['user'])
        full_name = m_user.first_name + " " + m_user.last_name
        my_task = Task.objects.get(id=item['id'])
        tem['id'] = item["id"]
        tem['user'] = full_name
        tem['description'] = item['description']
        tem['description2'] = item['description2']
        tem['date'] = date_jalali(item['date'], 2)
        tem['start_time'] = item['start_time'].strftime("%H:%M")
        tem['end_time'] = item['end_time'].strftime("%H:%M")
        tem['status'] = my_task.get_status_display()
        data.append(tem)

    return JsonResponse({"all_task": data})



class SubTasksList(ListView):
    model = Task
    template_name = 'task/list1.html'
    paginate_by = 10
    context_object_name = 'tasks'

    def get_queryset(self):
        if self.request.user.is_superuser:
            # exclude tasks which their orders are not published
            tasks = Task.published.all().order_by('-date').exclude(order__publish=False)
        else:
            tasks = Task.published.filter(user=self.request.user).order_by('-date').exclude(order__publish=False)

        q = self.request.GET.get('q')
        department = self.request.GET.get('department')
        status = self.request.GET.getlist('status')
        operation = self.request.GET.get('operation')
        subgroup = self.request.GET.get('subgroup')
        operator = self.request.GET.getlist('operator')
        dt_date = self.request.GET.get('dt_date')
        year = self.request.GET.get('year')

        if q:
            tasks = tasks.filter(order__orderId__contains=q)

        if department:
            tasks = tasks.filter(order__department_id=department)

        if status:
            orders = list(Order.objects.filter(task__in=tasks, status__in=status).values_list('id', flat=True))
            tasks = tasks.filter(order_id__in=orders)

        if operation:
            tasks = tasks.filter(order__operation=operation)

        if subgroup:
            tasks = tasks.filter(order__subGroup=subgroup)

        if operator != [''] and operator:
            tasks = tasks.filter(operators__in=operator)

        if dt_date:
            start_date, due_date = dt_date.split(' تا ')
            start_date = jdatetime.datetime.strptime(start_date, '%Y/%m/%d').togregorian().date()
            due_date = jdatetime.datetime.strptime(due_date, '%Y/%m/%d').togregorian().date()
            tasks = tasks.filter(Q(date__gte=start_date), Q(date__lte=due_date))

        tasks = tasks.order_by('-date')
        return tasks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        context['operations'] = Operation.objects.all()
        context['operators'] = User.objects.filter(groups__name='اپراتور فنی')
        status_choices = Order.StatusChoices
        context['status_choices'] = status_choices
        tasks = self.get_queryset()
        time_spent = 0
        for task in tasks:
            time_spent += task.get_time_diff

        context['time_spent'] = time_spent
        return context


def task_add(request):
    orderId = request.GET.get('orderId')
    if request.method == 'POST':
        description = request.POST.get('description')
        # description2 = request.POST.get('description2')
        orderId = request.POST.get('orderId')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        status = request.POST.get('status')
        operator_id = request.POST.getlist('operator')
        stuff_items = request.POST.get('stuff_items')
        if start_time > end_time:
            messages.error(request, 'ساعت شروع نمیتواند کمتر از ساعت پایان باشد')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if orderId:
            order = Order.published.get(orderId=orderId)
            operators = User.objects.filter(id__in=operator_id)
            task = Task.published.create(order=order, user=request.user, description=description)
            if stuff_items:
                stuff_items = stuff_items.split('|')
                for piece in stuff_items:
                    if piece:
                        try:
                            parsed_piece = piece.split(',')
                            piece_name = parsed_piece[0]
                            piece_count = int(parsed_piece[1])
                            piece_object = Part.objects.get(name=piece_name)
                            Piece.objects.create(count=piece_count, part=piece_object, order=order)
                        except ValueError:
                            pass
            year, month, day = split_persian_date(date)
            date = jdatetime.date(year, month, day).togregorian()

            task.date = date
            task.start_time = start_time
            task.end_time = end_time
            task.status = status
            task.operators.set(operators)
            task.save()

            task.order.status = status
            task.order.save()

            messages.success(request, 'درخواست شروع کار ثبت شد')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if orderId:
        order = Order.published.filter(orderId=orderId).last()
        operation = Operation.objects.get(name=order.operationName) if order.operationName else None
        department = Department.objects.get(name=order.departmentName) if order.departmentName else None
        parts = operation.parts.all() if operation else None
        stuff = department.stuffs.all() if department else None
        tasks = Task.published.filter(order=order).order_by('date')
    else:
        order = None
        parts = None
        tasks = None
        stuff = None
    operators = Group.objects.get(name='اپراتور فنی').user_set.all()
    status_choices = Order.StatusChoices
    context = {'order': order, 'tasks': tasks, 'operators': operators, 'status_choices': status_choices,
               'parts': parts if parts else stuff}
    return render(request, 'task/add.html', context)


@login_required(login_url='/users/login/')
def task_edit(request, taskId):
    task = Task.published.get(id=taskId)

    if request.method == 'POST':
        description = request.POST.get('description')
        description2 = request.POST.get('description2')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        status = request.POST.get('status')
        operators = request.POST.getlist('operator')

        start_time = start_time if start_time != '' else None
        end_time = end_time if end_time != '' else None

        if date != '-':
            year, month, day = split_persian_date(date)
            date = jdatetime.date(year, month, day).togregorian()
        else:
            date = None
        task.description = description
        task.description2 = description2
        task.date = date
        task.start_time = start_time
        task.end_time = end_time
        task.status = status
        task.operators.set(operators)
        if task.id == task.order.task.all().last().id:
            task.order.status = status
        else:
            task.order.status = task.order.task.last().status
        task.order.save()
        task.save()

        if status == '1':
            order = Order.published.get(task__id=taskId)
            order.isCompleted = True
            order.save()

        messages.success(request, f' کار با شماره سفارش {task.order.orderId} ویرایش شد')
        return redirect('tasks_list')

    operators = Group.objects.get(name='اپراتور فنی').user_set.all()
    status_choices = Order.StatusChoices
    context = {'task': task, 'operators': operators, 'status_choices': status_choices}
    return render(request, 'task/edit.html', context)


def task_detail(request, taskId):
    task = Task.published.get(id=taskId)
    context = {'task': task}
    return render(request, 'task/detail.html', context)


def task_invoice(request, taskId):
    task = Task.published.get(id=taskId)
    context = {'task': task}
    return render(request, 'task/invoice.html', context)


class DepartmentList(ListView):
    model = Department
    template_name = 'department/list.html'
    paginate_by = 1
    context_object_name = 'departments'


def department_add(request):
    if request.method == 'POST':

        name = request.POST.get('departmentName')
        if  Department.objects.filter(name=name).exists():
            messages.error(request,'با این نام قبلا ثبت شده است')
        else:
            Department.objects.get_or_create(name=name)
            messages.success(request, 'واحد ایجاد شد')
        # if Department.objects.filter(name=name).exists():
        #     messages.error(request,'با این نام قبلا ثبت شده است')
        return redirect('department_list')


def department_edit(request, departmentId):
    if request.method == 'POST':
        name = request.POST.get('departmentName')
        Department.objects.filter(id=departmentId).update(name=name)
        messages.success(request, 'واحد ویرایش شد')
        return redirect('department_list')


class OperationList(ListView):
    model = Operation
    template_name = 'operation/list.html'
    paginate_by = 10
    context_object_name = 'operations'

    def get_queryset(self):
        operation = Operation.objects.all().order_by('-created_at')
        q = self.request.GET.get('q')
        # print("q",q)
        if q:
            operation = Operation.objects.filter(Q(name__contains=q))

        return operation

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(OperationList, self).get_context_data()
        context['departments'] = Department.objects.all()
        context['stations'] = Station.objects.all()
        return context


def operation_add(request):
    if request.method == 'POST':
        name = request.POST.get('operationName')
        area_id = request.POST.get('area')
        station_id = request.POST.get('station')
        area = Department.objects.get(id=area_id)
        station = Station.objects.get(id=station_id)
        if Operation.objects.filter(name=name).exists():
            messages.error(request,'با این نام قبلا ماشین ثبت شده است')
        else:
            Operation.objects.get_or_create(name=name, area=area, station=station)
            messages.success(request, 'عملیات ایجاد شد')
        return redirect('operation_list')


def operation_edit(request, operationId):
    if request.method == 'POST':
        name = request.POST.get('operationName')
        station_id = request.POST.get('operationStation')
        station = Station.objects.get(id=station_id)
        area_id = request.POST.get('operationArea')
        area = Department.objects.get(id=area_id)
        Operation.objects.filter(id=operationId).update(name=name, station=station, area=area)
        messages.success(request, 'عملیات ویرایش شد')
        return redirect('operation_list')


class SubgroupList(ListView):
    model = Subgroup
    template_name = 'subgroup/list.html'
    paginate_by = 150
    context_object_name = 'subgroups'


def subgroup_add(request):
    if request.method == 'POST':
        name = request.POST.get('subgroupName')
        Subgroup.objects.get_or_create(name=name)
        messages.success(request, 'زیرگروه ایجاد شد')
        return redirect('subgroup_list')


def subgroup_edit(request, subgroupId):
    if request.method == 'POST':
        name = request.POST.get('subgroupName')
        Subgroup.objects.filter(id=subgroupId).update(name=name)
        messages.success(request, 'زیرگروه ویرایش شد')
        return redirect('subgroup_list')


class WorkReportView(ListView):
    # person per hour report
    template_name = "base/work_report.html"
    paginate_by = 10
    context_object_name = 'results'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.due_date = None
        self.tasks = None
        self.end_date = None
        self.start_date = None
        self.executor_name = None

    def get_queryset(self):
        self.executor_name = self.request.GET.get('executor_name')
        self.start_date = to_gregorian(self.request.GET.get('start_date'))
        self.due_date = to_gregorian(self.request.GET.get('due_date'))
        tasks = Task.objects.all()

        if self.start_date:
            tasks = tasks.filter(date__gte=self.start_date)
        if self.due_date:
            tasks = tasks.filter(date__lte=self.due_date)
        if self.executor_name:
            first_name, last_name = self.executor_name.split(' ')
            tasks = tasks.filter(user__first_name=first_name, user__last_name=last_name)

        return tasks

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        total_seconds = 0
        the_longest_work_seconds = 0
        the_longest_work_object = None
        if self.start_date or self.end_date or self.executor_name:
            for task in self.get_queryset():
                total_seconds = total_seconds_calculator(task, total_seconds)
                the_longest_work_seconds, the_longest_work_object = find_longest_work(task, the_longest_work_seconds,
                                                                                      the_longest_work_object)
                context['the_longest_operation'] = the_longest_work_object.order
            context['total_seconds'] = total_seconds
            context['the_longest_work'] = the_longest_work_seconds
        context['persons'] = Profile.mechanical_users.all()
        return context


class MachineReportView(ListView):
    model = Operation
    template_name = "base/machine_report.html"
    paginate_by = 10

    def get_queryset(self):
        operation_query = self.request.GET.get('operation')
        operations = Operation.objects.annotate(
            time_spent=Coalesce(
                Sum(F('order__task__end_time') - F('order__task__start_time'), output_field=DurationField())
                , timedelta(0, 0, 0), timedelta(0, 0, 0), output_field=DurationField()
            ),
        )
        time_spent = self.request.GET.get('time_spent')

        if operation_query:
            operations = operations.filter(name=operation_query)
        if time_spent == 'highest':
            operations = operations.order_by('-time_spent')
        elif time_spent == 'lowest':
            operations = operations.order_by('time_spent')

        return operations

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MachineReportView, self).get_context_data()
        context['all_operations'] = Operation.objects.all()
        return context


def seconds_to_time(raw_seconds):
    hours = int(raw_seconds // 3600)
    minutes = int((raw_seconds % 3600) // 60)
    # seconds = float((raw_seconds % 3600) % 60)
    hours_string = f"{f'{hours} ساعت ' if hours!=0 else ''}"
    minutes_string = f"{f'{minutes} دقیقه ' if minutes!=0 else ''}"
    # seconds_string = f"{f'{seconds} ثانیه ' if seconds!=0 else ''}"
    output = hours
    if output == '':
        output = 'فعالیتی پیدا نشد'
    return output


class ChartReportView(ListView):
    # person per hour report
    template_name = "chart/chart_report.html"
    # template_name = "index.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.due_date = None
        self.tasks = None
        self.end_date = None
        self.start_date = None
        self.executor_name = None

    def get_queryset(self):
        self.executor_name = self.request.GET.get('executor_name')
        self.start_date = to_gregorian(self.request.GET.get('start_date'))
        self.due_date = to_gregorian(self.request.GET.get('due_date'))
        tasks = Task.objects.all()

        if self.start_date:
            tasks = tasks.filter(date__gte=self.start_date)
        if self.due_date:
            tasks = tasks.filter(date__lte=self.due_date)
        if self.executor_name:
            first_name, last_name = self.executor_name.split(' ')
            tasks = tasks.filter(user__first_name=first_name, user__last_name=last_name)

        return tasks

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        all_user = Task.objects.values('operators__last_name')
        list_operators = []
        task_count = []
        sum_hours = []
        for item in all_user:
            if item["operators__last_name"] not in list_operators and item["operators__last_name"] is not None:
                list_operators.append(item["operators__last_name"])

                count = Task.objects.filter(operators__last_name=item["operators__last_name"]).count()
                task_count.append(count)

                tasks = Task.objects.filter(operators__last_name=item["operators__last_name"])
                time_spent=0
                for task in tasks:
                    time_spent += task.get_time_diff

                to_time = seconds_to_time(time_spent)
                sum_hours.append(to_time)

        context['time_spent'] = [1,2,3,4,5,6]

        context["operators"] = ['ali','mohammad','mahdi','hadi','kian','moktar']
        context["task_count"] = [1,2,3,4,5,6]

        return context


def change_task_publish_status(request, pk):
    if request.method == 'POST':
        if request.user.is_superuser:
            type_of_delete = request.POST.get('type_of_delete')
            from_detail_page = request.POST.get('detail')
            task = Task.published.get(pk=pk)
            if type_of_delete == 'delete_all':
                task.publish = False
                task.save()
                task.order.publish = False
                task.order.save()
            elif type_of_delete == 'delete_this':
                task.publish = False
                task.save()

            if from_detail_page:
                task.publish = False
                task.save()
                return redirect(reverse('task_detail', kwargs={'taskId': from_detail_page}))
            return redirect('tasks_list')
        else:
            return PermissionDenied()
    else:
        return redirect('tasks_list')


def change_part_publish_status(request, pk):
    if request.method == 'POST':
        if request.user.is_superuser:
            part = Part.objects.get(pk=pk)
            part.delete()
            return redirect('machine_parts_list')

        else:
            return PermissionDenied()
    else:
        return redirect('machine_parts_list')


def change_stuff_publish_status(request, pk):
    if request.method == 'POST':
        if request.user.is_superuser:
            stuff = Stuff.objects.get(pk=pk)
            stuff.delete()
            return redirect('stuff_list')

        else:
            return PermissionDenied()
    else:
        return redirect('stuff_list')


def change_station_publish_status(request, pk):
    if request.method == 'POST':
        if request.user.is_superuser:
            station = Station.objects.get(pk=pk)
            station.delete()
            return redirect('station_list')

        else:
            return PermissionDenied()
    else:
        return redirect('station_list')


def change_operation_publish_status(request, pk):
    if request.method == 'POST':
        if request.user.is_superuser:
            operation = Operation.objects.get(pk=pk)
            operation.delete()
            return redirect('operation_list')

        else:
            return PermissionDenied()
    else:
        return redirect('operation_list')


def change_order_publish_status(request, pk):
    if request.method == 'POST':

        if request.user.is_superuser:
            type_of_delete = request.POST.get('type_of_delete')
            order = Order.published.get(pk=pk)

            if type_of_delete == 'delete_all':
                order.publish = False
                order.save()
                order.task.all().update(publish=False)
                # order.task.all().save()

            elif type_of_delete == 'delete_this':
                order.publish = False
                order.save()

            return redirect('orders_list')

        else:
            return PermissionDenied()
    else:
        return redirect('orders_list')


def change_order_status(request, pk):
    order = Order.objects.get(pk=pk)
    if order.status == 'SV':
        order.status = 'SE'
        order.save()
        return HttpResponse(status=200)




class PartsList(ListView):
    model = Part
    template_name = 'base/parts_list.html'
    paginate_by = 10

    def get_queryset(self):
        part = Part.objects.all().order_by("-id")
        name = self.request.GET.get('name')
        machine = self.request.GET.get('machine')
        if name:
            part = part.filter(Q(name__contains=name))
        if machine:
            part = part.filter(Q(machine__name__contains=machine))

        return part


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PartsList, self).get_context_data()
        context['machines'] = Operation.objects.all()
        context['create_for'] = self.request.GET.get('create_for')
        return context

def machine_part_edit(request, part_id):
    if request.method == 'POST':
        part_name = request.POST.get('PartName')
        machine_id = request.POST.get('MachineName')
        machine = Operation.objects.get(id=machine_id)
        Part.objects.filter(id=part_id).update(name=part_name,machine=machine)
        messages.success(request, 'عملیات ویرایش شد')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # return redirect('parts')

def machine_part_add(request):
    if request.method == 'POST':
        machine_name = request.POST.get('machine')
        part_name = request.POST.get('part_name')
        # print("machine_name",machine_name)
        machine = Operation.objects.get(id=machine_name)
        if Part.objects.filter(machine_name=machine_name).exists():
            messages.error(request,'قطعه قبلا ثبت شده است')
        else:
            Part.objects.create(machine=machine, name=part_name)
            messages.success(request, 'با موفقیت ایجاد شد')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def machine_stuff_add(request):
    if request.method == 'POST':
        department_name = request.POST.get('department')
        stuff_name = request.POST.get('stuff_name')
        department = Department.objects.get(id=department_name)
        Stuff.objects.create(department=department, name=stuff_name)
        return redirect('stuff_list')


class StationList(ListView):
    model = Station
    template_name = 'base/station_list.html'


def station_add(request):
    if request.method == 'POST':
        station_name = request.POST.get('station_name')
        Station.objects.create(name=station_name)
        return redirect('station_list')


class StuffList(ListView):
    model = Stuff
    template_name = 'base/stuff_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['departments'] = Department.objects.all()
        # context['create_for'] = self.request.GET.get('create_for')
        return context
# class StuffEdit()


# class test(TemplateView):
#     template_name = 'order/change_password.html'











class ChartreportView(ListView):
    # person per hour report
    # template_name = "chart/chart_report.html"
    template_name = "index.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.due_date = None
        self.tasks = None
        self.end_date = None
        self.start_date = None
        self.executor_name = None

    def get_queryset(self):
        self.executor_name = self.request.GET.get('executor_name')
        self.start_date = to_gregorian(self.request.GET.get('start_date'))
        self.due_date = to_gregorian(self.request.GET.get('due_date'))
        tasks = Task.objects.all()

        if self.start_date:
            tasks = tasks.filter(date__gte=self.start_date)
        if self.due_date:
            tasks = tasks.filter(date__lte=self.due_date)
        if self.executor_name:
            first_name, last_name = self.executor_name.split(' ')
            tasks = tasks.filter(user__first_name=first_name, user__last_name=last_name)

        return tasks

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        all_user = Task.objects.values('operators__last_name')
        list_operators = []
        task_count = []
        sum_hours = []
        maximmum = []
        for item in all_user:
            if item["operators__last_name"] not in list_operators and item["operators__last_name"] is not None:
                list_operators.append(item["operators__last_name"])

                count = Task.objects.filter(operators__last_name=item["operators__last_name"]).count()
                task_count.append(count[:3])

                tasks = Task.objects.filter(operators__last_name=item["operators__last_name"])
                time_spent=0
                for task in tasks:
                    time_spent += task.get_time_diff

                to_time = seconds_to_time(time_spent)
                sum_hours.append(to_time)
                # for tasks in task_count:
                #     maximmum.append(max(tasks)[:3])

        context['time_spent'] = sum_hours

        context["opera"] = list_operators
        context["task_count"] = task_count
        context["max"] = maximmum

        return context

# 
# @login_required(login_url='/users/login/')
# def index(request):
#     user = request.user
#     tasks = None
#     all_department = Order.objects.values('department__name')
#     list_departement = []
#     order_count = []
#     list_machine = []
#     sum_hours = []
#     all_machine = Order.objects.values('operation__name')
#     last = Order.objects.all().order_by('-createdAt')[:10]
#     logo = Logo.objects.all()
#     task = Task.published.filter(order__status='WG')
#     orde = Order.published.all()
#     s = len(task)
#     b = len(orde)
#     if s or b == 0:
#         return render(request,'index.html')
#     else:
#         cala = round((s / b) * 100)
# 
#     # if (s / b) * 100 == 0:
#     #     cala = round((s / b) * 100)
#     #     print(cala)
#     # if round(((s / b) * 100)) == 0:
#     #     print(round(((len(task) / len(orde)) * 100)))
#     # cala = round(((len(task) / len(orde)) * 100))
#     # if cala > 0:
#     #     print(cala)
# 
# 
#     for tem in all_machine:
#         if tem["operation__name"] not in list_machine and tem["operation__name"] is not None:
#             tasks = Task.objects.filter(order__operation__name=tem["operation__name"])
#             time_spent = 0
#             for task in tasks:
#                 time_spent += task.get_time_diff
#             to_time = seconds_to_time(time_spent)
#             if to_time > 10:
#                 sum_hours.append(to_time)
#                 list_machine.append(tem["operation__name"])
#     for item in all_department:
#         if item["department__name"] not in list_departement and item["department__name"] is not None:
#             list_departement.append(item["department__name"])
# 
#             count = Order.objects.filter(department__name=item["department__name"]).count()
#             order_count.append(count)
# 
#             context = {'users': users, 'orders': orders, 'tasks': tasks,
#                        'tasks_done': tasks_done,
#                        'tasks_saved': tasks_saved,
#                        'tasks_seen': tasks_seen,
#                        'tasks_doing': tasks_doing,
#                        'tasks_waiting': tasks_waiting,
#                        'tasks_sent': tasks_sent, 'list_department': list_departement, 'order_count': order_count,
#                        'list_machine': list_machine, 'time_spent': sum_hours, 'order_last': last, 'logo': logo,
#                        'cal': cala
#                        }
#             return render(request, 'index.html', context)





def test(request):

    return render(request, 'review/detail1.html')