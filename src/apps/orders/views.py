from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from apps.orders.forms import UserOrderForm
from apps.orders.models import Order
from apps.orders.utils import is_staff_or_superuser, build_user_label
from django.contrib.auth import get_user_model

User = get_user_model()


class OrderCreateView(LoginRequiredMixin, CreateView):
    template_name = "orders/order_create.html"
    form_class = UserOrderForm
    model = Order

    def form_valid(self, form: UserOrderForm) -> HttpResponse:
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse("orders:detail", kwargs={"pk": self.object.pk})


class OrderListView(LoginRequiredMixin, ListView):
    template_name = "orders/order_list.html"
    model = Order
    context_object_name = "orders"
    paginate_by = 10

    ALLOWED_ORDERING = {
        "created_at",
        "-created_at",
    }

    def get_queryset(self) -> QuerySet[Order]:
        queryset = Order.objects.select_related("user")

        if not is_staff_or_superuser(self.request.user):
            queryset = queryset.filter(user=self.request.user)

        status = (self.request.GET.get("status") or "").strip()
        if status in Order.OrderStatus.values:
            queryset = queryset.filter(status=status)

        if is_staff_or_superuser(self.request.user):
            user_id = (self.request.GET.get("user") or "").strip()
            if user_id.isdigit():
                queryset = queryset.filter(user_id=int(user_id))

        ordering = self.get_ordering_param()

        return queryset.order_by(ordering, "-id")

    def get_ordering_param(self) -> str:
        ordering = (self.request.GET.get("ordering") or "-created_at").strip()

        if ordering not in self.ALLOWED_ORDERING:
            return "-created_at"

        return ordering

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Order.OrderStatus.choices
        context["ordering_choices"] = (
            ("-created_at", "Сначала новые"),
            ("created_at", "Сначала старые"),
        )
        context["selected_status"] = (self.request.GET.get("status") or "").strip()
        context["selected_ordering"] = self.get_ordering_param()
        context["selected_user"] = (self.request.GET.get("user") or "").strip()
        context["can_filter_by_user"] = is_staff_or_superuser(self.request.user)
        context["selected_user_label"] = ""

        if context["can_filter_by_user"] and context["selected_user"].isdigit():
            selected_user_obj = (
                User.objects.filter(pk=int(context["selected_user"]))
                .only("id", "username", "first_name", "last_name", "email")
                .first()
            )
            if selected_user_obj:
                context["selected_user_label"] = build_user_label(selected_user_obj)

        params = self.request.GET.copy()
        params.pop("page", None)
        params.pop("partial", None)
        context["querystring"] = params.urlencode()

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get("partial") == "1":
            self.template_name = "orders/partials/order_list_items.html"

        return super().render_to_response(context, **response_kwargs)


class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = "orders/order_detail.html"
    model = Order
    context_object_name = "order"

    def get_queryset(self) -> QuerySet[Order]:
        queryset = Order.objects.select_related("user")

        if is_staff_or_superuser(self.request.user):
            return queryset

        return queryset.filter(user=self.request.user)


def orders_root_redirect(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("orders:list")

    return redirect("users:login")


def users_autocomplete(request: HttpRequest) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)

    if not is_staff_or_superuser(request.user):
        return JsonResponse({"detail": "You do not have permission to perform this action."}, status=403)

    query = (request.GET.get("q") or "").strip()
    users_qs = User.objects.only("id", "username", "first_name", "last_name", "email")

    if query:
        users_qs = users_qs.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        )
    else:
        users_qs = users_qs.none()

    users = users_qs.order_by("last_name", "first_name", "username")[:20]
    payload = [{"id": user.id, "label": build_user_label(user)} for user in users]

    return JsonResponse({"results": payload})
