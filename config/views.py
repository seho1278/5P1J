from django.urls import reverse_lazy
from django.views.generic import RedirectView

class IndexRedirectView(RedirectView):
    url = reverse_lazy('movies:main')