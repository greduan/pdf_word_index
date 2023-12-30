import io
import os
import re
from collections import defaultdict

import cherrypy
import nltk
import PyPDF2
from nltk.corpus import words as corpus_words
from nltk.stem import PorterStemmer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

nltk.download("words")

english_words = corpus_words.words()


class Root(object):
    @cherrypy.expose
    def index(self):
        if cherrypy.request.cookie.get("logged-in"):
            raise cherrypy.HTTPRedirect("/upload")
        else:
            raise cherrypy.HTTPRedirect("/login")


@cherrypy.expose
class Login(object):
    @cherrypy.tools.accept(media="text/html")
    def GET(self):
        if cherrypy.request.cookie.get("logged-in"):
            raise cherrypy.HTTPRedirect("/upload")
        else:
            return open("templates/login.html")

    @cherrypy.expose
    def POST(self, password=None):
        if password == os.environ.get("PDF_WORD_INDEX_PASSWORD"):
            # Set 'logged-in' cookie for 1 hour
            cherrypy.response.cookie["logged-in"] = "1"
            cherrypy.response.cookie["logged-in"]["max-age"] = 3600
            raise cherrypy.HTTPRedirect("/upload")
        else:
            raise cherrypy.HTTPRedirect("/login")


@cherrypy.expose
class Upload(object):
    @cherrypy.tools.accept(media="text/html")
    def GET(self):
        if cherrypy.request.cookie.get("logged-in"):
            return open("templates/upload.html")
        else:
            raise cherrypy.HTTPRedirect("/login")

    @cherrypy.expose
    def POST(self, file):
        # Read PDF
        # Make word indexes

        reader = PyPDF2.PdfReader(file.file)
        index = {}
        for i in range(len(reader.pages)):
            text = reader.pages[i].extract_text()
            re_words = re.findall(
                r"\b\w+\b", text
            )  # Extract words, ignoring punctuation
            for word in re_words:
                word = word.lower()
                index.setdefault(word, []).append(i + 1)  # Page numbers are 1-indexed

        # Generate new PDF

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        story = []

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="TwoColumn", fontSize=10, leading=13))

        ## Add words to PDF

        ps = PorterStemmer()
        stem_index = defaultdict(list)
        for word, pages in index.items():
            if word not in english_words or not word.isalpha():
                continue

            stem = ps.stem(word)
            if stem not in stem_index:
                stem_index[stem] = {"words": [word], "pages": set(pages)}
            else:
                stem_index[stem]["words"].append(word)
                stem_index[stem]["pages"].update(set(pages))

        for stem in sorted(stem_index):
            words = ", ".join(sorted(stem_index[stem]["words"]))
            pages = ", ".join(map(str, sorted(list(stem_index[stem]["pages"]))))
            word_to_draw = f"<font size=12><b>{words},</b></font> " + pages
            ptext = "<font size=10>%s</font>" % word_to_draw.strip()
            story.append(Paragraph(ptext, styles["TwoColumn"]))
            story.append(Spacer(1, 12))

        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()

        cherrypy.response.headers["Content-Type"] = "application/pdf"
        cherrypy.response.headers[
            "Content-Disposition"
        ] = 'attachment; filename="index.pdf"'

        return pdf_data


if __name__ == "__main__":
    cherrypy.tree.mount(Root(), "/")
    cherrypy.tree.mount(
        Login(),
        "/login",
        {
            "/": {
                "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
                "tools.response_headers.on": True,
            }
        },
    )
    cherrypy.tree.mount(
        Upload(),
        "/upload",
        {
            "/": {
                "request.dispatch": cherrypy.dispatch.MethodDispatcher(),
                "tools.response_headers.on": True,
            }
        },
    )

    cherrypy.config.update(
        {"server.socket_host": "127.0.0.1", "server.socket_port": 8080}
    )
    cherrypy.engine.start()
    cherrypy.engine.block()
