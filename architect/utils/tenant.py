# architect/utils/tenant.py
from typing import Optional
from django.db.models import QuerySet, Q
import logging
logger = logging.getLogger(__name__)


def get_tenant(user) -> Optional[int]:
    """
    Returns the tenant/reflexo id for the authenticated user, or None.
    Be robust against stale user instances by refetching when needed.
    """
    if not getattr(user, 'is_authenticated', False):
        return None

    tenant_id = getattr(user, 'reflexo_id', None)
    if tenant_id is not None:
        return tenant_id

    # Fallback: refetch from DB in case the in-memory user is stale
    try:
        pk = getattr(user, 'pk', None)
        if pk:
            tenant_id = user.__class__.objects.filter(pk=pk).values_list('reflexo_id', flat=True).first()
            if tenant_id is None:
                logger.info("Tenant check: user id=%s has no reflexo assigned in DB.", pk)
            else:
                logger.info("Tenant check: user id=%s refetched reflexo_id=%s.", pk, tenant_id)
                return tenant_id
    except Exception:
        pass

    # Second fallback: some deployments store tenant on Clinica.UserProfile
    try:
        profile = getattr(user, 'clinica_profile', None)
        if profile is not None:
            tenant_id = getattr(profile, 'reflexo_id', None)
            if tenant_id is not None:
                logger.info("Tenant check: user id=%s resolved via clinica_profile reflexo_id=%s.", getattr(user, 'pk', None), tenant_id)
                return tenant_id
    except Exception:
        pass
    return None


def is_global_admin(user) -> bool:
    """Returns True if the user can bypass tenant filtering.

    Conditions:
    - Django superuser
    - Has explicit permission 'architect.view_all_tenants'
    - Or a legacy/custom attribute rol == 'Admin' (kept for backward compatibility)
    """
    if not getattr(user, 'is_authenticated', False):
        return False
    if getattr(user, 'is_superuser', False):
        return True
    # Check explicit Django permission that can be granted in admin
    try:
        if user.has_perm('architect.view_all_tenants'):
            return True
    except Exception:
        # In case auth backends are not fully configured, do not break
        pass
    # Fallback to legacy role field
    return getattr(user, 'rol', None) == 'Admin'


def filter_by_tenant(qs: QuerySet, user, field: str = 'reflexo') -> QuerySet:
    """
    Filters a queryset by the current user's tenant unless user is global admin.
    Assumes the model has a FK named given by 'field'.
    """
    if is_global_admin(user):
        return qs
    tenant_id = get_tenant(user)
    if tenant_id is None:
        # If no tenant, return empty queryset to avoid data leak
        return qs.none()
    return qs.filter(**{f"{field}_id": tenant_id})


def assign_tenant_on_create(data: dict, user, field: str = 'reflexo') -> dict:
    """
    Ensures the tenant is set in data for create operations if user is not global admin.
    Does not override if already set and admin.
    """
    if is_global_admin(user):
        return data
    tenant_id = get_tenant(user)
    # Only set if not present or different. Use *_id to avoid instance requirement
    data = dict(data)
    data[f"{field}_id"] = tenant_id
    return data


def filter_by_tenant_including_global(qs: QuerySet, user, field: str = 'reflexo') -> QuerySet:
    """
    Like filter_by_tenant, but also includes global defaults (where reflexo IS NULL).

    - Global admins bypass filtering (see is_global_admin)
    - If user has a tenant -> include records with that tenant OR reflexo IS NULL
    - If user has no tenant -> only include global (IS NULL) to avoid leaks
    """
    if is_global_admin(user):
        return qs
    tenant_id = get_tenant(user)
    if tenant_id is None:
        return qs.filter(**{f"{field}__isnull": True})
    return qs.filter(Q(**{f"{field}_id": tenant_id}) | Q(**{f"{field}__isnull": True}))
