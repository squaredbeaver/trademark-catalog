import re
from datetime import date
from logging import Logger
from typing import Optional
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from pydantic import BaseModel


class ApplicationContent:
    def __init__(self, root: Element, namespaces: dict[str, str]):
        self._root = root
        self._namespaces = namespaces

    @classmethod
    def create_from_application_node(
            cls,
            application_node: Element,
            namespaces: dict[str, str],
    ) -> 'ApplicationContent':
        content_node = application_node.find(
            './TradeMarkTransactionBody/TransactionContentDetails/TransactionData/TradeMarkDetails/TradeMark',
            namespaces=namespaces,
        )
        if content_node is None:
            raise ValueError("No content")

        return cls(root=content_node, namespaces=namespaces)

    def is_word_trademark(self) -> bool:
        mark_feature_node = self._root.find("./MarkFeature", namespaces=self._namespaces)
        mark_feature = self._extract_text(mark_feature_node)

        if mark_feature == 'Word':
            return True

        return False

    def get_title(self) -> Optional[str]:
        title_node = self._root.find(
            './WordMarkSpecification/MarkVerbalElementText',
            namespaces=self._namespaces,
        )
        return self._extract_text(title_node)

    def get_description(self) -> Optional[str]:
        description_node = self._root.find(
            "./GoodsServicesDetails/GoodsServices/ClassDescriptionDetails/"
            "ClassDescription/GoodsServicesDescription[@languageCode='en']",
            namespaces=self._namespaces,
        )
        return self._extract_text(description_node)

    def get_application_number(self) -> Optional[str]:
        application_number_node = self._root.find("./ApplicationNumber", namespaces=self._namespaces)
        return self._extract_text(application_number_node)

    def get_application_date(self) -> Optional[str]:
        application_date_node = self._root.find("./ApplicationDate", namespaces=self._namespaces)
        return self._extract_text(application_date_node)

    def get_registration_date(self) -> Optional[str]:
        registration_date_node = self._root.find("./RegistrationDate", namespaces=self._namespaces)
        return self._extract_text(registration_date_node)

    def get_expiry_date(self) -> Optional[str]:
        expiry_date_node = self._root.find("./ExpiryDate", namespaces=self._namespaces)
        return self._extract_text(expiry_date_node)

    @staticmethod
    def _extract_text(node: Optional[Element]) -> Optional[str]:
        if node is not None:
            return node.text

        return None


class ParseApplicationRequest(BaseModel):
    application_xml: str


class ApplicationParsingResult(BaseModel):
    title: Optional[str]
    description: Optional[str]
    application_number: Optional[str]
    application_date: Optional[date]
    registration_date: Optional[date]
    expiry_date: Optional[date]

    def is_valid(self) -> bool:
        return self.title is not None and self.registration_date is not None


class ParseApplicationResponse(BaseModel):
    success: bool
    application: Optional[ApplicationParsingResult]

    def is_success(self) -> bool:
        return self.success and self.application is not None

    @classmethod
    def success_response(cls, application: ApplicationParsingResult) -> 'ParseApplicationResponse':
        return cls(success=True, application=application)

    @classmethod
    def error_response(cls) -> 'ParseApplicationResponse':
        return cls(success=False)


class TrademarkApplicationParserService:
    def __init__(
            self,
            logger: Logger,
    ):
        self._logger = logger
        self._namespace_regex = re.compile(r"\{(.*?)}")

    def parse_application(self, request: ParseApplicationRequest) -> ParseApplicationResponse:
        try:
            application_node = ElementTree.fromstring(request.application_xml)
        except ElementTree.ParseError as parsing_error:
            self._logger.error('Cannot parse application: %s', parsing_error)
            return ParseApplicationResponse.error_response()

        namespaces = self._get_namespaces(application_node)

        try:
            content = ApplicationContent.create_from_application_node(application_node, namespaces)
        except ValueError as content_parsing_error:
            self._logger.error('Cannot read application content: %s', content_parsing_error)
            return ParseApplicationResponse.error_response()

        if not content.is_word_trademark():
            self._logger.debug('Non-word trademark')
            return ParseApplicationResponse.error_response()

        result = ApplicationParsingResult(
            title=content.get_title(),
            description=content.get_description(),
            application_number=content.get_application_number(),
            application_date=content.get_application_date(),
            registration_date=content.get_registration_date(),
            expiry_date=content.get_expiry_date(),
        )
        return ParseApplicationResponse.success_response(result)

    def _get_namespaces(self, node: Element) -> dict[str, str]:
        match = re.findall(self._namespace_regex, node.tag)

        if not match:
            return {}

        return {'': match[0]}
