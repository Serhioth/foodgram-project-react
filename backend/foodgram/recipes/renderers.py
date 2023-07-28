from rest_framework.renderers import BaseRenderer

from recipes.shopping_cart import make_pdf


class PdfRenderer(BaseRenderer):
    """Custom renderer for accepting application/pdf headers"""
    media_type = 'application/pdf'
    format = 'pdf'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        pdf = make_pdf(data['ingredient_amount_list'])
        return pdf
