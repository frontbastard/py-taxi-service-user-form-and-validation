from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import (
    DriverCreateForm,
    DriverUpdateForm,
    CarForm,
    DriverLicenseUpdateForm
)
from .models import Driver, Car, Manufacturer


@login_required
def index(request):
    """View function for the home page of the site."""

    num_drivers = Driver.objects.count()
    num_cars = Car.objects.count()
    num_manufacturers = Manufacturer.objects.count()

    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_drivers": num_drivers,
        "num_cars": num_cars,
        "num_manufacturers": num_manufacturers,
        "num_visits": num_visits + 1,
    }

    return render(request, "taxi/index.html", context=context)


class ManufacturerListView(LoginRequiredMixin, generic.ListView):
    model = Manufacturer
    context_object_name = "manufacturer_list"
    template_name = "taxi/manufacturer_list.html"
    paginate_by = 5


class ManufacturerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Manufacturer
    fields = "__all__"
    success_url = reverse_lazy("taxi:manufacturer-list")


class ManufacturerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Manufacturer
    fields = "__all__"
    success_url = reverse_lazy("taxi:manufacturer-list")


class ManufacturerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Manufacturer
    success_url = reverse_lazy("taxi:manufacturer-list")


class CarListView(LoginRequiredMixin, generic.ListView):
    model = Car
    paginate_by = 5
    queryset = Car.objects.all().select_related("manufacturer")


class CarDetailView(LoginRequiredMixin, generic.DetailView):
    model = Car


class CarCreateView(LoginRequiredMixin, generic.CreateView):
    model = Car
    form_class = CarForm
    success_url = reverse_lazy("taxi:car-list")


class CarUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Car
    form_class = CarForm
    success_url = reverse_lazy("taxi:car-list")


class CarDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Car
    success_url = reverse_lazy("taxi:car-list")


class DriverListView(LoginRequiredMixin, generic.ListView):
    model = get_user_model()
    paginate_by = 5


class DriverDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    queryset = Driver.objects.all().prefetch_related("cars__manufacturer")


class DriverCreateView(LoginRequiredMixin, generic.CreateView):
    model = get_user_model()
    form_class = DriverCreateForm
    success_url = reverse_lazy("taxi:driver-list")


class DriverUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = get_user_model()
    form_class = DriverUpdateForm

    def get_success_url(self):
        return reverse_lazy(
            "taxi:driver-detail", kwargs={"pk": self.object.pk}
        )


class DriverDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = get_user_model()
    success_url = reverse_lazy("taxi:driver-list")


class DriverToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        car = get_object_or_404(Car, pk=pk)
        driver = request.user

        if car.drivers.filter(id=driver.id).exists():
            car.drivers.remove(driver)
        else:
            car.drivers.add(driver)

        return redirect("taxi:car-detail", pk=pk)


class DriverLicenseUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = get_user_model()
    form_class = DriverLicenseUpdateForm

    def get_success_url(self):
        return reverse_lazy(
            "taxi:driver-detail", kwargs={"pk": self.object.pk}
        )
