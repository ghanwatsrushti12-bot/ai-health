from __future__ import annotations

from django import forms

from apps.accounts.forms import BootstrapFormMixin

from .models import Feedback


class FeedbackForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["category", "doctor", "rating", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4}),
            "rating": forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["doctor"].required = False
        self._apply_bootstrap()
        self.fields["rating"].widget.attrs["class"] = "form-check-input"
