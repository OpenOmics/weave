import pandas as pd
from labkey.api_wrapper import APIWrapper


class LabKeyServer:
    api = None

    def __init__(self, domain, container_path, context_path, use_ssl) -> None:
        self.api = APIWrapper(domain, container_path, context_path, use_ssl=use_ssl)

    