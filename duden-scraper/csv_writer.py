from csv import DictWriter


class CSVWriter:
    delimiter = ";"

    def __init__(self, output_path: str, fields: list[str]):
        self.output_path = output_path
        self.fields = fields
        self._write_header()

    def _write_header(self):
        # pylint: disable=unspecified-encoding
        with open(self.output_path, "x"):
            pass
        header = {field: field for field in self.fields}
        self.writerow(header)

    def writerow(self, row: dict[str, str]) -> None:
        if not set(row) == set(self.fields):
            raise ValueError(f"Row {row} not compatible with CSV file format.")

        with open(self.output_path, "a", encoding="utf-8") as csv_file:
            DictWriter(
                csv_file,
                delimiter=self.delimiter,
                fieldnames=self.fields,
            ).writerow(row)
