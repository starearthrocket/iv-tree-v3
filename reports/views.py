from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import TreeReportForm


@login_required
def report_create(request):
    """Allow a logged-in user to submit a new tree report."""

    if request.method == 'POST':
        form = TreeReportForm(request.POST, request.FILES)

        if form.is_valid():
            report = form.save(commit=False)
            report.owner = request.user
            report.save()

            messages.success(
                request,
                'Your tree report has been submitted successfully.'
            )

            return redirect('core:home')
    else:
        form = TreeReportForm()

    return render(
        request,
        'reports/report_form.html',
        {'form': form},
    )