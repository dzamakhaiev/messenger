from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.backends import default_backend
import datetime
import ipaddress

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"UA"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"KIEV"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"KIEV"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"KFC"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"messenger.kfc"),
])).add_extension(
    x509.SubjectAlternativeName(
        [x509.DNSName(u"messenger.kfc"), x509.DNSName(u"localhost"),
         x509.IPAddress(ipaddress.IPv4Address(u"192.168.50.100"))]),
    critical=False,
).sign(private_key, hashes.SHA256(), default_backend())

one_day = datetime.timedelta(1, 0, 0)
certificate = x509.CertificateBuilder().subject_name(
    csr.subject
).issuer_name(
    csr.subject
).public_key(
    csr.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.today() - one_day
).not_valid_after(
    datetime.datetime.today() + (one_day * 365)
).add_extension(
    x509.SubjectAlternativeName([x509.DNSName(u"messenger.kfc"), x509.DNSName(u"localhost"),
         x509.IPAddress(ipaddress.IPv4Address(u"192.168.50.100"))]),

    critical=False,
).sign(private_key, hashes.SHA256(), default_backend())

with open("private_key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=NoEncryption()
    ))

with open("certificate.pem", "wb") as f:
    f.write(certificate.public_bytes(encoding=Encoding.PEM))
