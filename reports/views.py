from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProgressUpdateForm, TreeReportForm
from .models import TreeReport


def report_list(request):
    """Display public tree reports, newest first."""

    reports = TreeReport.objects.filter(
        visibility=TreeReport.Visibility.PUBLIC
    )

    return render(
        request,
        'reports/report_list.html',
        {'reports': reports},
    )


def report_detail(request, pk):
    """Display a public report or a private report to its owner."""

    report = get_object_or_404(TreeReport, pk=pk)

    if (
        report.visibility != TreeReport.Visibility.PUBLIC
        and report.owner != request.user
    ):
        raise Http404

    return render(
        request,
        'reports/report_detail.html',
        {'report': report},
    )


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

            return redirect(
                'reports:report_detail',
                pk=report.pk,
            )
    else:
        form = TreeReportForm()

    return render(
        request,
        'reports/report_form.html',
        {
            'form': form,
            'report': None,
        },
    )


@login_required
def report_edit(request, pk):
    """Allow only the report owner to edit their report."""

    report = get_object_or_404(
        TreeReport,
        pk=pk,
        owner=request.user,
    )

    if request.method == 'POST':
        form = TreeReportForm(
            request.POST,
            request.FILES,
            instance=report,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Your tree report has been updated successfully.'
            )

            return redirect(
                'reports:report_detail',
                pk=report.pk,
            )
    else:
        form = TreeReportForm(instance=report)

    return render(
        request,
        'reports/report_form.html',
        {
            'form': form,
            'report': report,
        },
    )


@login_required
def report_delete(request, pk):
    """Allow only the report owner to delete their report."""

    report = get_object_or_404(
        TreeReport,
        pk=pk,
        owner=request.user,
    )

    if request.method == 'POST':
        report.delete()

        messages.success(
            request,
            'Your tree report has been deleted.'
        )

        return redirect('reports:report_list')

    return render(
        request,
        'reports/report_confirm_delete.html',
        {'report': report},
    )


@login_required
def progress_create(request, pk):
    """Allow a report owner to add a progress update."""

    report = get_object_or_404(
        TreeReport,
        pk=pk,
        owner=request.user,
    )

    if request.method == 'POST':
        form = ProgressUpdateForm(request.POST, request.FILES)

        if form.is_valid():
            update = form.save(commit=False)
            update.tree_report = report
            update.author = request.user
            update.save()

            if update.status:
                report.status = update.status
                report.save(update_fields=['status', 'updated_at'])

            messages.success(
                request,
                'Progress update added successfully.'
            )

            return redirect(
                'reports:report_detail',
                pk=report.pk,
            )
    else:
        form = ProgressUpdateForm()

    return render(
        request,
        'reports/progress_form.html',
        {
            'form': form,
            'report': report,
        },
    )