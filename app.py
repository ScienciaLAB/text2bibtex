import argparse
import os
import sys

import httpx

GROBID_URL = os.environ.get("GROBID_URL", "https://lfoppiano-grobid-dev-full.hf.space")
GROBID_TIMEOUT = int(os.environ.get("GROBID_TIMEOUT", "30"))


def parse_citation(citation: str) -> str:
    """Send a free-text citation to GROBID and return BibTeX."""
    citation = citation.strip()
    if not citation:
        raise ValueError("Empty citation.")

    resp = httpx.post(
        f"{GROBID_URL}/api/processCitation",
        data={"citations": citation},
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

    def _gradio_parse(citation: str) -> str:
        try:
            return parse_citation(citation)
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
        gr.Markdown("Paste a free-text citation and get BibTeX output, powered by [GROBID](https://github.com/kermitt2/grobid).")

        citation_input = gr.Textbox(
            label="Citation",
            placeholder="Smith, J. (2020). Machine Learning Approaches. Journal of AI, 12(3), 45-67.",
            lines=3,
        )
        convert_btn = gr.Button("Convert", variant="primary")
        bibtex_output = gr.Code(label="BibTeX", language=None, lines=8)

        convert_btn.click(fn=_gradio_parse, inputs=citation_input, outputs=bibtex_output)
        citation_input.submit(fn=_gradio_parse, inputs=citation_input, outputs=bibtex_output)

        gr.Examples(
            examples=[
                ["Smith, J. (2020). Machine Learning Approaches. Journal of AI, 12(3), 45-67."],
                ["Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). Attention is all you need. Advances in neural information processing systems, 30."],
                ["LeCun, Y., Bengio, Y., & Hinton, G. Deep learning. Nature 521, 436-444 (2015)."],
            ],
            inputs=citation_input,
        )

    return demo


def __getattr__(name):
    """Lazy-load `demo` so HF Spaces finds it on import, but CLI stays lightweight."""
    if name == "demo":
        demo = _build_demo()
        globals()["demo"] = demo
        return demo
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def cli():
    parser = argparse.ArgumentParser(
        description="Convert free-text citations to BibTeX via GROBID.",
    )
    parser.add_argument(
        "citation",
        nargs="*",
        help="Citation string(s). If omitted, reads from stdin (one citation per line).",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Launch the Gradio web UI instead.",
    )
    args = parser.parse_args()

    if args.serve:
        _build_demo().launch(server_name="0.0.0.0")
        return

    # Collect citations from args or stdin
    if args.citation:
        citations = [" ".join(args.citation)]
    elif not sys.stdin.isatty():
        citations = [line for line in sys.stdin if line.strip()]
    else:
        parser.print_help()
        sys.exit(1)

    errors = 0
    for citation in citations:
        try:
            print(parse_citation(citation))
        except (ValueError, httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            errors += 1

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    cli()
