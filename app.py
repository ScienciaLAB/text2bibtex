import argparse
import os
import sys

import httpx

GROBID_URL = os.environ.get("GROBID_URL", "https://lfoppiano-grobid-dev-full.hf.space")
GROBID_TIMEOUT = int(os.environ.get("GROBID_TIMEOUT", "30"))


def parse_citation(citation: str, consolidate: bool = False) -> str:
    """Send a free-text citation to GROBID and return BibTeX."""
    citation = citation.strip()
    if not citation:
        raise ValueError("Empty citation.")

    data = {"citations": citation}
    if consolidate:
        data["consolidateCitations"] = "1"

    resp = httpx.post(
        f"{GROBID_URL}/api/processCitation",
        data=data,
        headers={"Accept": "application/x-bibtex"},
        timeout=GROBID_TIMEOUT,
    )
    resp.raise_for_status()

    bibtex = resp.text.strip()
    if not bibtex:
        raise ValueError("GROBID could not parse this citation.")

    return bibtex


def _build_demo():
    import gradio as gr

    def _gradio_parse(citation: str, consolidate: bool) -> str:
        try:
            return parse_citation(citation, consolidate=consolidate)
        except ValueError as e:
            raise gr.Error(str(e))
        except httpx.ConnectError:
            raise gr.Error("Cannot connect to GROBID service.")
        except httpx.TimeoutException:
            raise gr.Error("GROBID request timed out.")
        except httpx.HTTPStatusError as e:
            raise gr.Error(f"GROBID returned status {e.response.status_code}.")

    with gr.Blocks(title="Citation to BibTeX") as demo:
        gr.Markdown("# Citation to BibTeX")
        gr.Markdown('Paste a free-text citation and get BibTeX output, powered by <a href="https://github.com/grobidOrg/grobid" target="_blank">GROBID</a>.')

        with gr.Row():
            with gr.Column(scale=2):
                citation_input = gr.Textbox(
                    label="Citation",
                    placeholder="Smith, J. (2020). Machine Learning Approaches. Journal of AI, 12(3), 45-67.",
                    lines=3,
                )
                consolidate_toggle = gr.Checkbox(label="Consolidate (CrossRef lookup)", value=False)
                convert_btn = gr.Button("Convert", variant="primary")
                bibtex_output = gr.Code(label="BibTeX", language=None, lines=8)

            with gr.Column(scale=1):
                gr.Markdown(
                    "### Convert directly from your browser\n\n"
                    "Highlight a citation on any page, click the bookmark, and the BibTeX is copied to your clipboard.\n\n"
                    "**How to install:**\n"
                    "1. Copy the code below\n"
                    "2. Create a new bookmark in your browser\n"
                    "3. Paste the code as the bookmark URL\n\n"
                    "```\n"
                    "javascript:void(function(){var G='https://lfoppiano-grobid-dev-full.hf.space',t=window.getSelection().toString().trim();"
                    "if(!t){T('Select a citation first',1);return}T('Converting...');"
                    "fetch(G+'/api/processCitation',{method:'POST',headers:{Accept:'application/x-bibtex'},"
                    "body:new URLSearchParams({citations:t,consolidateCitations:'1'})})"
                    ".then(function(r){if(!r.ok)throw new Error('GROBID '+r.status);return r.text()})"
                    ".then(function(b){b=b.trim();if(!b)throw new Error('Could not parse citation');"
                    "return navigator.clipboard.writeText(b).then(function(){T('BibTeX copied!')})})"
                    ".catch(function(e){T(e.message,1)});"
                    "function T(m,err){var e=document.getElementById('_bt');if(e)e.remove();"
                    "e=document.createElement('div');e.id='_bt';e.textContent=m;"
                    "e.style.cssText='position:fixed;bottom:24px;right:24px;z-index:2147483647;"
                    "padding:12px 20px;border-radius:8px;font:14px/1.4 system-ui,sans-serif;"
                    "color:%23fff;background:'+(err?'%23c0392b':'%232ecc71')+';box-shadow:0 4px 12px rgba(0,0,0,.3);"
                    "transition:opacity .3s;opacity:1';document.body.appendChild(e);"
                    "setTimeout(function(){e.style.opacity='0';setTimeout(function(){e.remove()},300)},3000)}}())\n"
                    "```\n\n"
                    "**How to use:** select a citation on any webpage, then click the bookmark. "
                    "A green toast confirms the BibTeX was copied to your clipboard."
                )

        inputs = [citation_input, consolidate_toggle]
        convert_btn.click(fn=_gradio_parse, inputs=inputs, outputs=bibtex_output)
        citation_input.submit(fn=_gradio_parse, inputs=inputs, outputs=bibtex_output)

        gr.Examples(
            examples=[
                ["Smith, J. (2020). Machine Learning Approaches. Journal of AI, 12(3), 45-67."],
                ["Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). Attention is all you need. Advances in neural information processing systems, 30."],
                ["LeCun, Y., Bengio, Y., & Hinton, G. Deep learning. Nature 521, 436-444 (2015)."],
            ],
            inputs=citation_input,
        )

    return demo


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert free-text citations to BibTeX via GROBID.",
    )
    parser.add_argument(
        "citation",
        nargs="*",
        help="Citation string(s). If omitted, launches the web UI.",
    )
    parser.add_argument(
        "-c", "--consolidate",
        action="store_true",
        help="Consolidate results via CrossRef lookup.",
    )
    args = parser.parse_args()

    if args.citation:
        errors = 0
        citations = [" ".join(args.citation)]
        for citation in citations:
            try:
                print(parse_citation(citation, consolidate=args.consolidate))
            except (ValueError, httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
                print(f"ERROR: {e}", file=sys.stderr)
                errors += 1
        if errors:
            sys.exit(1)
    else:
        _build_demo().launch()
