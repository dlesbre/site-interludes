from django.db import models


class HTMLPageModel(models.Model):
    """modèle pour contenu de pages dynamiques
    (notamment home et faq)"""

    name = models.CharField(
        verbose_name="nom",
        unique=True,
        max_length=20,
    )
    slug = models.SlugField(
        verbose_name="url",
        blank=True,
        unique=True,
        help_text="Url de la page (laisser vide pour la page d'acceuil)",
    )
    content = models.TextField(
        help_text="Contenu de la page (au format HTML, avec les balises templates django)",
    )
    visible = models.BooleanField(
        default=True,
        help_text="Décochez pour cacher la page sans pour autant la supprimer",
    )

    def path(self) -> str:
        if self.slug is None or self.slug == "":
            return "/"
        return "/" + self.slug + "/"

    path.__name__ = "chemin d'accès"

    def __str__(self) -> str:
        return self.path()

    class Meta:
        verbose_name = "page HTML"
        verbose_name_plural = "pages HTML"
        ordering = ["slug"]
