from apps.links.models import Link


def generate_fake_links(owner, start=1, count=1, is_external=False):
    for i in range(start, start + count):
        if is_external:
            url = "https://testsite%d.com" % i
        else:
            url = "https://testsite%d.dstl.gov.uk" % i
        link = Link(
            name="Test Tool %d" % i,
            description='How do you describe a tool like tool %d?' % i,
            destination=url,
            owner=owner,
            is_external=is_external
        )
        link.save()
        yield link
