import django.dispatch

status_changed = django.dispatch.Signal(
    providing_args=['order', 'new_status', 'old_status']
)
