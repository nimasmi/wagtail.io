from operator import attrgetter

from django.db import models
from django.shortcuts import redirect

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

from wagtail.wagtailcore.models import Page, Orderable

from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, MultiFieldPanel, InlinePanel,
    PageChooserPanel, StreamFieldPanel
)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailsnippets.models import register_snippet

from wagtail.wagtailsearch import index


from wagtailio.utils.blocks import StoryBlock
from wagtailio.utils.models import (
    SocialMediaMixin,
    CrossPageMixin,
)


# Carousel items

class HomePageMainCarouselItem(Orderable, models.Model):
    page = ParentalKey('core.HomePage', related_name='main_carousel_items')
    tab_title = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    summary = models.CharField(max_length=511)
    image = models.ForeignKey(
        'images.WagtailIOImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    video = models.URLField()
    call_to_action_internal_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    call_to_action_external_link = models.URLField("Call to action URL", blank=True)
    call_to_action_caption = models.CharField(max_length=255, blank=True)

    @property
    def call_to_action_link(self):
        if self.call_to_action_internal_link:
            return self.call_to_action_internal_link.url
        else:
            return self.call_to_action_external_link

    panels = [
        FieldPanel('tab_title'),
        FieldPanel('title'),
        FieldPanel('summary'),
        ImageChooserPanel('image'),
        FieldPanel('video'),
        MultiFieldPanel([
            PageChooserPanel('call_to_action_internal_link'),
            FieldPanel('call_to_action_external_link'),
            FieldPanel('call_to_action_caption')
        ], "Call To Action")
    ]


class HomePageSecondaryCarouselItem(Orderable, models.Model):
    page = ParentalKey('core.HomePage', related_name='secondary_carousel_items')
    title = models.CharField(max_length=255)
    desktop_image = models.ForeignKey(
        'images.WagtailIOImage',
        related_name='+'
    )
    mobile_image = models.ForeignKey(
        'images.WagtailIOImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    blockquote = models.TextField()
    author_name = models.CharField(max_length=255)
    author_image = models.ForeignKey(
        'images.WagtailIOImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    author_job = models.CharField(max_length=255)
    website = models.URLField(blank=True)

    panels = [
        FieldPanel('title'),
        ImageChooserPanel('desktop_image'),
        ImageChooserPanel('mobile_image'),
        FieldPanel('blockquote'),
        FieldPanel('author_name'),
        ImageChooserPanel('author_image'),
        FieldPanel('author_job'),
        FieldPanel('website')
    ]


# Homepage

class HomePage(Page, SocialMediaMixin, CrossPageMixin):
    secondary_carousel_introduction = models.CharField(max_length=511)

HomePage.content_panels = Page.content_panels + [
    InlinePanel(HomePage, 'main_carousel_items', label="Main carousel items"),
    FieldPanel('secondary_carousel_introduction'),
    InlinePanel(HomePage, 'secondary_carousel_items', label="Secondary carousel items"),
]

HomePage.promote_panels = Page.promote_panels + SocialMediaMixin.panels + CrossPageMixin.panels


# Blog index

class BlogIndexPage(Page, SocialMediaMixin, CrossPageMixin):
    def serve(self, request):
        latest_blog = BlogPage.objects.all().order_by('-date').first()
        return redirect(latest_blog.url)


BlogIndexPage.content_panels = Page.content_panels + [

]

BlogIndexPage.promote_panels = Page.promote_panels + SocialMediaMixin.panels + CrossPageMixin.panels


# Blog page

class Author(models.Model):
    name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255, blank=True)
    image = models.ForeignKey(
        'images.WagtailIOImage',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    url = models.URLField(blank=True)

    def __str__(self):
        return self.name

    panels = [
        FieldPanel('name'),
        FieldPanel('job_title'),
        ImageChooserPanel('image'),
        FieldPanel('url')
    ]

register_snippet(Author)


class BlogPage(Page, SocialMediaMixin, CrossPageMixin):
    author = models.ForeignKey(
        'core.Author',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+')
    main_image = models.ForeignKey(
        'images.WagtailIOImage',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    date = models.DateField()
    introduction = models.CharField(max_length=511)
    body = StreamField(StoryBlock())

    @property
    def siblings(self):
        return self.__class__.objects.live(
        ).sibling_of(self).order_by('-date')

BlogPage.content_panels = Page.content_panels + [
    SnippetChooserPanel('author', Author),
    ImageChooserPanel('main_image'),
    FieldPanel('date'),
    FieldPanel('introduction'),
    StreamFieldPanel('body')
]

BlogPage.promote_panels = Page.promote_panels + SocialMediaMixin.panels + CrossPageMixin.panels


# Standard content page

class StandardPage(Page, SocialMediaMixin, CrossPageMixin):
    introduction = models.CharField(max_length=511)
    body = StreamField(StoryBlock())

StandardPage.content_panels = Page.content_panels + [
    FieldPanel('introduction'),
    StreamFieldPanel('body')
]

StandardPage.promote_panels = Page.promote_panels + SocialMediaMixin.panels + CrossPageMixin.panels


# Feature page

class Bullet(Orderable, models.Model):
    snippet = ParentalKey('core.FeatureAspect', related_name='bullets')
    title = models.CharField(max_length=255)
    text = RichTextField()

    panels = [
        FieldPanel('title'),
        FieldPanel('text')
    ]


class FeatureAspect(ClusterableModel):
    title = models.CharField(max_length=255)
    screenshot = models.ForeignKey(
        'images.WagtailIOImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def __str__(self):
        return self.title

FeatureAspect.panels = [
    FieldPanel('title'),
    InlinePanel(FeatureAspect, 'bullets', label="Bullets"),
    ImageChooserPanel('screenshot')
]

register_snippet(FeatureAspect)


class FeaturePageFeatureAspect(Orderable, models.Model):
    page = ParentalKey('core.FeaturePage', related_name='feature_aspects')
    feature_aspect = models.ForeignKey('core.FeatureAspect', related_name='+')

    panels = [
        SnippetChooserPanel('feature_aspect', FeatureAspect)
    ]


class FeaturePage(SocialMediaMixin, CrossPageMixin, Page):
    introduction = models.CharField(max_length=255)

    @property
    def feature_index(self):
        return FeatureIndexPage.objects.ancestor_of(
            self
        ).order_by('-depth').first()

    @property
    def previous(self):
        if self.get_prev_sibling():
            return self.get_prev_sibling()
        else:
            return self.get_siblings().last()

    @property
    def next(self):
        if self.get_next_sibling():
            return self.get_next_sibling()
        else:
            return self.get_siblings().first()

FeaturePage.content_panels = Page.content_panels + [
    FieldPanel('introduction'),
    InlinePanel(FeaturePage, 'feature_aspects', label="Feature Aspects")
]

FeaturePage.promote_panels = Page.promote_panels + SocialMediaMixin.panels + CrossPageMixin.panels

# Feature Index Page

class FeatureIndexPageMenuOption(models.Model):
    page = ParentalKey('core.FeatureIndexPage',
                       related_name='secondary_menu_options')
    link = models.ForeignKey(
        'wagtailcore.Page',
        related_name='+'
    )
    label = models.CharField(max_length=255)

    panels = [
        PageChooserPanel('link'),
        FieldPanel('label')
    ]


class FeatureIndexPage(Page):
    introduction = models.CharField(max_length=255)

    @property
    def features(self):
        return self.get_children().live().type(FeaturePage)

FeatureIndexPage.content_panels = Page.content_panels + [
    FieldPanel('introduction'),
    InlinePanel(FeatureIndexPage,
                'secondary_menu_options',
                label="Secondary Menu Options")
]


# Developers Page

class DevelopersPageOptions(Orderable, models.Model):
    page = ParentalKey('core.DevelopersPage', related_name='options')
    icon = models.CharField(max_length=255,
                            choices=(('fa-github', 'Github'),
                                     ('fa-google', 'Google'),
                                     ('fa-eye', 'Eye'),
                                     ('fa-server', 'Servers')))
    title = models.CharField(max_length=255)
    summary = models.CharField(max_length=255)
    internal_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    external_link = models.URLField("External link", blank=True)

    @property
    def link(self):
        if self.internal_link:
            return self.internal_link.url
        else:
            return self.external_link

    panels = [
        FieldPanel('icon'),
        FieldPanel('title'),
        FieldPanel('summary'),
        MultiFieldPanel([
            PageChooserPanel('internal_link'),
            FieldPanel('external_link')
        ], "Link")
    ]


class DevelopersPage(Page, SocialMediaMixin, CrossPageMixin):
    introduction = models.CharField(max_length=255)
    body_heading = models.CharField(max_length=255)

DevelopersPage.content_panels = Page.content_panels + [
    FieldPanel('introduction'),
    FieldPanel('body_heading'),
    InlinePanel(DevelopersPage, 'options', label="Options")
]


# Newsletter signups

class NewsletterEmailAddress(models.Model):
    email = models.EmailField()
