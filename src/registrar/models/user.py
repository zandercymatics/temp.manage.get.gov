import logging

from django.contrib.auth.models import AbstractUser
from django.db import models

from .domain_invitation import DomainInvitation
from registrar.models import TransitionDomain
from registrar.models import DomainInformation

from phonenumber_field.modelfields import PhoneNumberField  # type: ignore


logger = logging.getLogger(__name__)


class User(AbstractUser):
    """
    A custom user model that performs identically to the default user model
    but can be customized later.
    """

    # #### Constants for choice fields ####
    RESTRICTED = "restricted"
    STATUS_CHOICES = ((RESTRICTED, RESTRICTED),)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=None,  # Set the default value to None
        null=True,  # Allow the field to be null
        blank=True,  # Allow the field to be blank
    )

    domains = models.ManyToManyField(
        "registrar.Domain",
        through="registrar.UserDomainRole",
        related_name="users",
    )

    phone = PhoneNumberField(
        null=True,
        blank=True,
        help_text="Phone",
        db_index=True,
    )

    def __str__(self):
        # this info is pulled from Login.gov
        if self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''} {self.email or ''}"
        elif self.email:
            return self.email
        else:
            return self.username

    def restrict_user(self):
        self.status = self.RESTRICTED
        self.save()

    def unrestrict_user(self):
        self.status = None
        self.save()

    def is_restricted(self):
        return self.status == self.RESTRICTED

    def first_login(self):
        """Callback when the user is authenticated for the very first time.

        When a user first arrives on the site, we need to retrieve any domain
        invitations that match their email address.
        """
        for invitation in DomainInvitation.objects.filter(
            email=self.email, status=DomainInvitation.INVITED
        ):
            try:
                invitation.retrieve()
                invitation.save()
            except RuntimeError:
                # retrieving should not fail because of a missing user, but
                # if it does fail, log the error so a new user can continue
                # logging in
                logger.warn(
                    "Failed to retrieve invitation %s", invitation, exc_info=True
                )
        
        transition_domain_exists = TransitionDomain.objects.filter(
            username=self.email
        ).exists()
        if transition_domain_exists:
            # Looks like the user logged in with the same e-mail as
            # a corresponding transition domain.  Create a Domain
            # Information object.
            # TODO: Do we need to check for existing Domain Info objects?
            # TODO: Should we add a Domain to the DomainInfo object?
            # NOTE that adding a user role for this user
            # as admin for this domain is already done
            # in the incitation.retrieve() method. So
            # we don't need to do that here.
           new_domain_info = DomainInformation(creator=self)
           new_domain_info.save()

    class Meta:
        permissions = [
            ("analyst_access_permission", "Analyst Access Permission"),
            ("full_access_permission", "Full Access Permission"),
        ]
