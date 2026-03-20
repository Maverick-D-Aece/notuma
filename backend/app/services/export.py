import io
import zipfile
from typing import List, Dict, Any
from PIL import Image
from backend.app.services.composition import CompositionService
from backend.app.utils.storage import storage_client

class ExportService:
    def __init__(self):
        self.composition_service = CompositionService()

    def generate_page_image(self, layout_data: Dict[str, Any], format: str = "PNG") -> io.BytesIO:
        """Issue 5.1: High-resolution exports per page."""
        # For high-res, we could scale the dimensions in layout_data if needed
        return self.composition_service.render_page(layout_data)

    def create_cbz(self, pages: List[Dict[str, Any]]) -> io.BytesIO:
        """Issue 5.3: Comic Book Archive (CBZ) packaging."""
        cbz_buffer = io.BytesIO()
        with zipfile.ZipFile(cbz_buffer, 'w', zipfile.ZIP_DEFLATED) as cbz:
            for i, page_layout in enumerate(pages):
                img_buffer = self.generate_page_image(page_layout)
                cbz.writestr(f"page_{i+1:03d}.png", img_buffer.getvalue())

        cbz_buffer.seek(0)
        return cbz_buffer

    def create_pdf(self, pages: List[Dict[str, Any]]) -> io.BytesIO:
        """Issue 5.3: PDF packaging."""
        pdf_buffer = io.BytesIO()
        images = []
        for page_layout in pages:
            img_buffer = self.generate_page_image(page_layout)
            img = Image.open(img_buffer)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            images.append(img)

        if images:
            images[0].save(pdf_buffer, format='PDF', save_all=True, append_images=images[1:])

        pdf_buffer.seek(0)
        return pdf_buffer

    def create_epub(self, pages: List[Dict[str, Any]], title: str = "Manga Export") -> io.BytesIO:
        """Issue 5.2: Fixed-Layout EPUB export pipeline."""
        # This is a simplified version of EPUB generation.
        # A real implementation would use 'ebooklib' or manually create the structure.
        epub_buffer = io.BytesIO()
        with zipfile.ZipFile(epub_buffer, 'w', zipfile.ZIP_DEFLATED) as epub:
            # mimetype (must be first and uncompressed)
            epub.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

            # META-INF/container.xml
            container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""
            epub.writestr("META-INF/container.xml", container_xml)

            # OEBPS/content.opf (Fixed-layout metadata)
            manifest = ""
            spine = ""
            for i in range(len(pages)):
                manifest += f'    <item id="page{i+1}" href="page{i+1}.xhtml" media-type="application/xhtml+xml"/>\n'
                manifest += f'    <item id="img{i+1}" href="img{i+1}.png" media-type="image/png"/>\n'
                spine += f'    <itemref idref="page{i+1}"/>\n'

            content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="pub-id" version="3.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{title}</dc:title>
        <dc:language>en</dc:language>
        <dc:identifier id="pub-id">notuma-{title.lower().replace(' ', '-')}</dc:identifier>
        <meta property="rendition:layout">pre-paginated</meta>
        <meta property="rendition:orientation">auto</meta>
        <meta property="rendition:spread">auto</meta>
    </metadata>
    <manifest>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
{manifest}
    </manifest>
    <spine toc="ncx">
{spine}
    </spine>
</package>"""
            epub.writestr("OEBPS/content.opf", content_opf)

            # OEBPS/toc.ncx (Table of Contents)
            toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head><meta name="dtb:uid" content="pub-id"/></head>
    <docTitle><text>{title}</text></docTitle>
    <navMap>
        <navPoint id="navpoint-1" playOrder="1">
            <navLabel><text>Start</text></navLabel>
            <content src="page1.xhtml"/>
        </navPoint>
    </navMap>
</ncx>"""
            epub.writestr("OEBPS/toc.ncx", toc_ncx)

            # Pages and Images
            for i, page_layout in enumerate(pages):
                img_buffer = self.generate_page_image(page_layout)
                epub.writestr(f"OEBPS/img{i+1}.png", img_buffer.getvalue())

                # Simple XHTML wrapper for the image
                page_xhtml = f"""<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
    <head>
        <title>Page {i+1}</title>
        <meta name="viewport" content="width=1200, height=1800"/>
    </head>
    <body style="margin:0;padding:0;">
        <img src="img{i+1}.png" style="width:100%;height:100%;"/>
    </body>
</html>"""
                epub.writestr(f"OEBPS/page{i+1}.xhtml", page_xhtml)

        epub_buffer.seek(0)
        return epub_buffer

export_service = ExportService()
