import logging
import random
from faker import Faker

from registrar.models import (
    User,
    DomainApplication,
    DraftDomain,
    Contact,
    Website,
)

fake = Faker()
logger = logging.getLogger(__name__)


class DomainApplicationFixture:
    """
    Load domain applications into the database.

    Make sure this class' `load` method is called from `handle`
    in management/commands/load.py, then use `./manage.py load`
    to run this code.
    """

    # any fields not specified here will be filled in with fake data or defaults
    # NOTE BENE: each fixture must have `organization_name` for uniqueness!
    # Here is a more complete example as a template:
    # {
    #     "status": "started",
    #     "organization_name": "Example - Just started",
    #     "organization_type": "federal",
    #     "federal_agency": None,
    #     "federal_type": None,
    #     "address_line1": None,
    #     "address_line2": None,
    #     "city": None,
    #     "state_territory": None,
    #     "zipcode": None,
    #     "urbanization": None,
    #     "purpose": None,
    #     "anything_else": None,
    #     "is_policy_acknowledged": None,
    #     "authorizing_official": None,
    #     "submitter": None,
    #     "other_contacts": [],
    #     "current_websites": [],
    #     "alternative_domains": [],
    # },
    DA = [
        {
            "status": "started",
            "organization_name": "Example - Finished but not Submitted",
        },
        {
            "status": "submitted",
            "organization_name": "Example - Submitted but pending Investigation",
        },
        {
            "status": "in review",
            "organization_name": "Example - In Investigation",
        },
        {
            "status": "in review",
            "organization_name": "Example - Approved",
        },
        {
            "status": "withdrawn",
            "organization_name": "Example - Withdrawn",
        },
        {
            "status": "action needed",
            "organization_name": "Example - Action Needed",
        },
        {
            "status": "rejected",
            "organization_name": "Example - Rejected",
        },
    ]

    @classmethod
    def fake_contact(cls):
        return {
            "first_name": fake.first_name(),
            "middle_name": None,
            "last_name": fake.last_name(),
            "title": fake.job(),
            "email": fake.ascii_safe_email(),
            "phone": "201-555-5555",
        }

    @classmethod
    def fake_dot_gov(cls):
        return f"{fake.slug()}.gov"

    @classmethod
    def _set_non_foreign_key_fields(cls, da: DomainApplication, app: dict):
        """Helper method used by `load`."""
        da.status = app["status"] if "status" in app else "started"
        da.organization_type = app["organization_type"] if "organization_type" in app else "federal"
        da.federal_agency = (
            app["federal_agency"]
            if "federal_agency" in app
            # Random choice of agency for selects, used as placeholders for testing.
            else random.choice(DomainApplication.AGENCIES)  # nosec
        )

        da.federal_type = (
            app["federal_type"]
            if "federal_type" in app
            else random.choice(["executive", "judicial", "legislative"])  # nosec
        )
        da.address_line1 = app["address_line1"] if "address_line1" in app else fake.street_address()
        da.address_line2 = app["address_line2"] if "address_line2" in app else None
        da.city = app["city"] if "city" in app else fake.city()
        da.state_territory = app["state_territory"] if "state_territory" in app else fake.state_abbr()
        da.zipcode = app["zipcode"] if "zipcode" in app else fake.postalcode()
        da.urbanization = app["urbanization"] if "urbanization" in app else None
        da.purpose = app["purpose"] if "purpose" in app else fake.paragraph()
        da.anything_else = app["anything_else"] if "anything_else" in app else None
        da.is_policy_acknowledged = app["is_policy_acknowledged"] if "is_policy_acknowledged" in app else True

    @classmethod
    def _set_foreign_key_fields(cls, da: DomainApplication, app: dict, user: User):
        """Helper method used by `load`."""
        if not da.investigator:
            da.investigator = User.objects.get(username=user.username) if "investigator" in app else None

        if not da.authorizing_official:
            if "authorizing_official" in app and app["authorizing_official"] is not None:
                da.authorizing_official, _ = Contact.objects.get_or_create(**app["authorizing_official"])
            else:
                da.authorizing_official = Contact.objects.create(**cls.fake_contact())

        if not da.submitter:
            if "submitter" in app and app["submitter"] is not None:
                da.submitter, _ = Contact.objects.get_or_create(**app["submitter"])
            else:
                da.submitter = Contact.objects.create(**cls.fake_contact())

        if not da.requested_domain:
            if "requested_domain" in app and app["requested_domain"] is not None:
                da.requested_domain, _ = DraftDomain.objects.get_or_create(name=app["requested_domain"])
            else:
                da.requested_domain = DraftDomain.objects.create(name=cls.fake_dot_gov())

    @classmethod
    def _set_many_to_many_relations(cls, da: DomainApplication, app: dict):
        """Helper method used by `load`."""
        if "other_contacts" in app:
            for contact in app["other_contacts"]:
                da.other_contacts.add(Contact.objects.get_or_create(**contact)[0])
        elif not da.other_contacts.exists():
            other_contacts = [
                Contact.objects.create(**cls.fake_contact()) for _ in range(random.randint(0, 3))  # nosec
            ]
            da.other_contacts.add(*other_contacts)

        if "current_websites" in app:
            for website in app["current_websites"]:
                da.current_websites.add(Website.objects.get_or_create(website=website)[0])
        elif not da.current_websites.exists():
            current_websites = [
                Website.objects.create(website=fake.uri()) for _ in range(random.randint(0, 3))  # nosec
            ]
            da.current_websites.add(*current_websites)

        if "alternative_domains" in app:
            for domain in app["alternative_domains"]:
                da.alternative_domains.add(Website.objects.get_or_create(website=domain)[0])
        elif not da.alternative_domains.exists():
            alternative_domains = [
                Website.objects.create(website=cls.fake_dot_gov()) for _ in range(random.randint(0, 3))  # nosec
            ]
            da.alternative_domains.add(*alternative_domains)

    @classmethod
    def load(cls):
        """Creates domain applications for each user in the database."""
        logger.info("Going to load %s domain applications" % len(cls.DA))
        try:
            users = list(User.objects.all())  # force evaluation to catch db errors
        except Exception as e:
            logger.warning(e)
            return

        for user in users:
            logger.debug("Loading domain applications for %s" % user)
            for app in cls.DA:
                try:
                    da, _ = DomainApplication.objects.get_or_create(
                        creator=user,
                        organization_name=app["organization_name"],
                    )
                    cls._set_non_foreign_key_fields(da, app)
                    cls._set_foreign_key_fields(da, app, user)
                    da.save()
                    cls._set_many_to_many_relations(da, app)
                except Exception as e:
                    logger.warning(e)


class DomainFixture(DomainApplicationFixture):

    """Create one domain and permissions on it for each user."""

    @classmethod
    def load(cls):
        try:
            users = list(User.objects.all())  # force evaluation to catch db errors
        except Exception as e:
            logger.warning(e)
            return

        for user in users:
            # approve one of each users in review status domains
            application = DomainApplication.objects.filter(creator=user, status=DomainApplication.IN_REVIEW).last()
            logger.debug(f"Approving {application} for {user}")
            application.approve()
            application.save()
