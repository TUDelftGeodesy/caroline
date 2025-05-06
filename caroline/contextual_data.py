import datetime as dt
import os
import sys

import requests

from caroline.config import get_config

CONFIG = get_config()


def fetch_url_contextual_data(url: str) -> list:
    """Retrieve contextual data from a URL over the internet.

    The content of the URL is returned as a whole. Lines are split and stripped of spurious whitespace.

    Parameters
    ----------
    url: str
        The link to the website containing the contextual data

    Returns
    -------
    list
        List containing the contents of the url in strings, one entry per line
    """
    data = requests.get(url)

    if 400 <= data.status_code <= 599:  # these are error responses
        raise ValueError(f"Please check your input url, received error code {data.status_code} for URL: {url}")

    if 300 <= data.status_code <= 399:  # these are redirect messages
        raise ValueError(f"Please check your input url, received redirect code {data.status_code} for URL: {url}")

    contents = data.text  # if the call did not return an error message, we read the text and format it
    content_lines = [c.strip() for c in contents.split("\n")]
    return content_lines


def update_contextual_data(verbose: bool) -> None:
    """Update the contextual data as defined in `config/contextual-data-definitions.yaml`.

    Parameters
    ----------
    verbose: bool
        Whether or not to print updates to stdout

    """
    contextual_data_definitions = get_config(
        f"{CONFIG['CAROLINE_INSTALL_DIRECTORY']}/config/contextual-data-definitions.yaml", flatten=False
    )

    timestamp = dt.datetime.now().strftime("%Y%m%d")

    for definition in contextual_data_definitions.keys():
        if verbose:
            os.system(f'''echo "Starting {definition} update..."''')
        os.makedirs(f"{CONFIG['CAROLINE_CONTEXTUAL_DATA_DIRECTORY']}/{definition}", exist_ok=True)

        if "url" in contextual_data_definitions[definition].keys():
            data = fetch_url_contextual_data(contextual_data_definitions[definition]["url"])

            output_file = (
                f"{CONFIG['CAROLINE_CONTEXTUAL_DATA_DIRECTORY']}/{definition}/{definition}-{timestamp}."
                f"{contextual_data_definitions[definition]['output-format']}"
            )
            link_file = (
                f"{CONFIG['CAROLINE_CONTEXTUAL_DATA_DIRECTORY']}/{definition}/{definition}-latest."
                f"{contextual_data_definitions[definition]['output-format']}"
            )

            with open(output_file, "w") as f:
                for line in data:
                    f.write(f"{line}\n")

            os.system(f"ln -sfn {output_file} {link_file}")

        else:
            raise ValueError(
                "Unhandled contextual data mode! " f"Got keys {contextual_data_definitions[definition].keys()}"
            )

        if verbose:
            os.system(f'''echo "Finished {definition} update!"''')


if __name__ == "__main__":
    verbose = False

    argv = sys.argv

    if len(argv) == 2:  # a verbose argument was passed
        if argv[1] == "verbose":
            verbose = True

    update_contextual_data(verbose)
