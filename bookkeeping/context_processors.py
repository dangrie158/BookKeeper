from bookkeeping.models import BookEntry


def years_processor(request):
    if request.user.is_authenticated:
        queryset = BookEntry.objects.filter(user=request.user)
        years = sorted(set(queryset.values_list("booking_date__year", flat=True)), reverse=True)
        return {"years_with_entries": years}
    return {}
