import json
import os
import time

from prompt_toolkit import prompt
from rich.console import Console
from rich.prompt import Prompt

# Change the annotator name below.
ANNOTATOR = "Your Name"
WORD_LIMIT = 25

def list_documents(data_dir, result_dir):
    documents, annotated = {}, {}
    for filename in os.listdir(data_dir):
        pid = filename.split('.')[0]
        annotated[pid] = os.path.exists(os.path.join(result_dir, filename))
        with open(os.path.join(data_dir, filename), 'r') as file:
            data = json.load(file)
            documents[pid] = data
    return documents, annotated

def ask_with_limit(message, limit=WORD_LIMIT):
    while True:
        value = prompt(message)
        length = len(value.split())
        if length <= limit:
            return value
        print(f"Please enter a value less than {limit} words. You entered {length} words.")

def annotate_document(document):
    console = Console()
    console.clear()
    console.print(f"Title: {document['title']}", style="green")
    abstract = document['abstract'].replace('\n', ' ')
    console.print(f"Abstract: {abstract}", style="yellow")

    start_time = time.time()
    console.print(
        "\nContext: [i]The status quo of related literature or reality which motivated this study. This could normally be a problem or a research gap that has not been successfully addressed by previous work..[/i]",
        style="magenta")
    context = ask_with_limit("Enter context:\n")

    console.print(
        "\nKey Idea: [i]The main intellectual merit of this paper, often in comparison to the context. This could normally be a novel idea or solution proposed in this paper that distincts it from what’s already done in literature.[/i]",
        style="magenta")
    key_idea = ask_with_limit("Enter key idea:\n")

    console.print(
        "\nMethod: [i]The specific method that investigates and validates the key idea. This could be a theoretical framework, an experimental setup, or other necessary methodology to implement and/or evaluate the key idea.[/i]",
        style="magenta")
    method = ask_with_limit("Enter method:\n")

    console.print(
        "\nOutcome: [i]The factual statement about the study output. This could be the experiment results and any other measurable outcome. It marks whether the key hypothesis is testified or not.[/i]",
        style="magenta")
    outcome = ask_with_limit("Enter outcome:\n")

    console.print(
        "\nProjected Impact: [i]The author-anticipated impact of the work on the field, and potential further research identified by the author that may improve or extend this study.[/i]",
        style="magenta")
    projected_impact = ask_with_limit("Enter projected impact:\n")

    used_time = time.time() - start_time
    annotations = {
        'context': context,
        'key idea': key_idea,
        'method': method,
        'outcome': outcome,
        'projected impact': projected_impact,
    }
    document.update(annotations)
    document['used time'] = used_time
    document['annotator'] = ANNOTATOR
    return document


def save_annotation(result_dir, pid, annotated_document):
    filepath = os.path.join(result_dir, f"{pid}.json")
    with open(filepath, 'w') as file:
        json.dump(annotated_document, file, indent=4)


def main():
    data_dir = 'data'
    result_dir = 'result'
    os.makedirs(result_dir, exist_ok=True)
    documents, annotated = list_documents(data_dir, result_dir)

    console = Console()
    console.clear()
    if all(annotated.values()):
        console.print("No documents need annotation.", style="red")
        return

    console.print("Select a document to annotate: [red]red[/red] for unannotated, [green]green[/green] for annotated.")
    console.print("Use `Ctrl+C` to exit.\n")
    for i, (pid, doc) in enumerate(documents.items(), 1):
        is_annotated = annotated[pid]
        console.print(f"{i}\t{doc['title']}",
                      style="green" if is_annotated else "red")

    choice = Prompt.ask(
        "\nEnter the number of the document",
        choices=[str(i) for i in range(1,
                                       len(documents) + 1)],
        show_choices=False,
    )
    pid = list(documents.keys())[int(choice) - 1]
    annotated_document = annotate_document(documents[pid])
    save_annotation(result_dir, pid, annotated_document)
    console.print("\nDocument has been annotated and saved.", style="blue")


if __name__ == "__main__":
    try:
        while True:
            main()
    except KeyboardInterrupt:
        print("\nFinished annotation.")
