import numpy as np
from datetime import datetime
import pytz
from PIL import Image
from pydicom import Dataset, read_file, dcmwrite, FileDataset
from pydicom.uid import (
    generate_uid,
    ImplicitVRLittleEndian,
    PYDICOM_IMPLEMENTATION_UID,
)
from pynetdicom import AE

# from pynetdicom.sop_class import SecondaryCaptureImageStorage
from pynetdicom.sop_class import DigitalXRayImageStorageForPresentation
import tempfile
import os
import random


def get_timezone():
    # Verifica se a variável de ambiente TZ está definida
    if "TZ" in os.environ:
        # Se estiver definida, usa o valor da variável de ambiente
        return pytz.timezone(os.environ["TZ"])
    else:
        # Se não estiver definida, usa o fuso horário "America/Fortaleza"
        return pytz.timezone("America/Fortaleza")


# Função para obter a data atual no formato DICOM
def get_current_date():
    current_date = datetime.now(get_timezone())
    return current_date.strftime("%Y%m%d")


# Função para obter a hora atual no formato DICOM
def get_current_time():
    current_date = datetime.now(get_timezone())
    return current_date.strftime("%H%M%S.%f")


def calculate_birth_date(age):
    # Obtenha o ano atual
    current_year = datetime.now(get_timezone()).year

    # Subtraia a idade do ano atual para obter o ano de nascimento
    birth_year = current_year - age

    # Defina a data de nascimento como 1º de janeiro do ano de nascimento
    birth_date = datetime(birth_year, 1, 1)

    return birth_date


def read_image(image_path, conv_grayscale=False, conv_rgb=False):
    # Ler a imagem PNG
    image = Image.open(image_path)
    # Converter a imagem para escala de cinza
    if conv_grayscale:
        image = image.convert("L")
    elif conv_rgb:
        image = image.convert("RGB")
    return image


def create_dicom(
    image_path, output, modality, region, metadata, conv_grayscale=False, conv_rgb=False
):
    print(f"Image input path: {image_path}")
    print(f"DCM output path: {output}")
    # Leia a imagem e armazene os dados de pixel
    img = read_image(image_path, conv_grayscale, conv_rgb)
    pixel_array = np.array(img)

    # Crie um novo dataset DICOM
    ds = Dataset()
    ds.file_meta = Dataset()
    ds.file_meta.FileMetaInformationGroupLength = 206
    ds.file_meta.FileMetaInformationVersion = b"\x00\x01"
    ds.file_meta.MediaStorageSOPClassUID = (
        DigitalXRayImageStorageForPresentation  # "1.2.840.10008.5.1.4.1.1.1.1"
    )
    ds.file_meta.MediaStorageSOPInstanceUID = (
        generate_uid()
    )  # ("1.3.51.0.7.1209738733.5000.23372.38822.58758.64857.30388")
    ds.file_meta.ImplementationClassUID = (
        generate_uid()
    )  # "1.2.276.0.7238010.5.0.3.5.4"
    ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian
    ds.file_meta.ImplementationVersionName = "OSIRIX"
    ds.file_meta.SourceApplicationEntityTitle = "AIHEALTH"
    #     (0002, 0000) File Meta Information Group Length  UL: 206
    # (0002, 0001) File Meta Information Version       OB: b'\x00\x01'
    # (0002, 0002) Media Storage SOP Class UID         UI: Digital X-Ray Image Storage - For Presentation
    # (0002, 0003) Media Storage SOP Instance UID      UI: 1.3.51.0.7.1209738733.5000.23372.38822.58758.64857.30388
    # (0002, 0010) Transfer Syntax UID                 UI: Implicit VR Little Endian
    # (0002, 0012) Implementation Class UID            UI: 1.2.276.0.7238010.5.0.3.5.4
    # (0002, 0013) Implementation Version Name         SH: 'OSIRIX'
    # (0002, 0016) Source Application Entity Title     AE: 'AIHEALTH'

    # ds.TransferSyntaxUID = ExplicitVRLittleEndian
    ds.SOPClassUID = (
        DigitalXRayImageStorageForPresentation  # "1.2.840.10008.5.1.4.1.1.1.1"
    )
    # Gerar novos UID para StudyInstanceUID, SeriesInstanceUID e SOPInstanceUID
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SOPInstanceUID = generate_uid()

    # Defina os atributos DICOM com base nas informações de metadados
    ds.PatientID = str(metadata["Patient ID"])
    ds.PatientName = f"Robot {str(metadata['Patient ID'])}"
    # ds.PatientAge = str(metadata["Patient Age"])
    # Calcule a data de nascimento com base na idade
    birth_date = calculate_birth_date(metadata["Patient Age"])
    # Defina o valor do atributo PatientBirthDate
    ds.PatientBirthDate = birth_date.strftime("%Y%m%d")
    ds.PatientSex = metadata["Patient Gender"]
    ds.Modality = modality  # Modalidade de imagem
    ds.ViewPosition = metadata["View Position"]
    ds.InstanceNumber = 1
    ds.StudyDescription = region
    ds.InstanceComments = metadata["Finding Labels"]
    ds.Findings = metadata["Finding Labels"]
    ds.Interpretation = metadata["Finding Labels"]
    ds.PatientDiagnosis = metadata["Finding Labels"]
    ds.SeriesDescription = f"{region} {metadata['View Position']}"
    current_date = get_current_date()
    current_time = get_current_time()
    ds.StudyDate = current_date
    ds.StudyTime = current_time
    ds.SeriesDate = current_date
    ds.SeriesTime = current_time
    ds.AcquisitionDate = current_date
    ds.AcquisitionTime = current_time
    # Defina os atributos obrigatórios
    ds.is_little_endian = True
    ds.is_implicit_VR = True

    # ds.Rows, ds.Columns = metadata["OriginalImage[Width"], metadata["Height]"]
    ds.Rows, ds.Columns = pixel_array.shape[0], pixel_array.shape[1]
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    if img.mode == "L":
        ds.PhotometricInterpretation = "MONOCHROME2"
    else:
        ds.PhotometricInterpretation = "RGB"
    ds.PixelData = pixel_array.tobytes()

    # Salve o dataset DICOM em um arquivo DCM
    # dcm_filename = os.path.splitext(os.path.basename(image_path))[0] + ".dcm"
    # ds.save_as(dcm_filename)
    ds.save_as(output)  # , write_like_original=True)
    print(ds)
    # ds.save_as("output.dcm")

    return ds


def gen_random_dcm(df, paths):
    MODALITY = os.environ["MODALITY"]

    idx = random.randint(0, len(df) - 1)
    img_ds = df.loc[idx]
    print(img_ds)
    with tempfile.NamedTemporaryFile(suffix=".dcm", delete=True) as fp:
        print(f"path: {fp.name}")
        ds = create_dicom(
            paths[img_ds["Image Index"]],
            fp.name,
            MODALITY,
            "TORAX",
            img_ds,
            conv_grayscale=False,
            conv_rgb=False,
        )
        # ds_test = create_dicom_test()
        # ds_test.save_as("example.dcm")
        send_to_server(
            os.environ["AETITLE"],
            os.environ["REMOTE_ADDRESS"],
            int(os.environ["REMOTE_PORT"]),
            ds,
            fp.name,  # "example.dcm",  # "IM-0001-0001.dcm",
        )
        print(f"**********************************")
        print(f"FINDING LABELS: {img_ds['Finding Labels']}")
        print(f"**********************************")


def create_dicom_test():
    ds = Dataset()

    # Defina os atributos obrigatórios
    ds.PatientName = "John Doe"
    ds.PatientID = "123456"
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.1.1"
    # ds.SOPClassUID = generate_uid()
    ds.SOPInstanceUID = generate_uid()
    ds.Modality = "DX"
    ds.PatientSex = "M"
    ds.PatientAge = "50"
    ds.StudyDescription = "Chest X-Ray"
    ds.BodyPartExamined = "Chest"
    ds.Manufacturer = "Manufacturer"
    ds.is_little_endian = True
    ds.is_implicit_VR = True
    ds.file_meta = Dataset()
    ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian
    ds.PixelData = b"\x00\x00\x00\x00"  # Dados do pixel, necessário para o atributo, pode ser qualquer coisa

    return ds


def send_to_server(aetitle, remote_address, remote_port, ds, fpath):
    print(f"AETITLE: {aetitle} REMOTE: {remote_address}:{remote_port}")
    print(f"File: {fpath}")
    dcm = read_file(fpath, force=True)
    # dcm = read_file(fpath)
    ae = AE(ae_title=aetitle)

    # # Conecta-se ao Orthanc
    ae.add_requested_context(DigitalXRayImageStorageForPresentation)

    # Defina as informações do servidor Orthanc
    # ae.add_requested_context(
    #     "1.2.840.10008.5.1.4.1.1.7"
    # )  # Secondary Capture Image Storage
    # ae.add_requested_context(
    #     "1.2.840.10008.5.1.4.1.1.77.1.4.1"
    # )  # Digital X-Ray Image Storage - For Presentation
    # ae.add_requested_context(
    #     "1.2.840.10008.5.1.4.1.1.88.22"
    # )  # Enhanced XA Image Storage
    # ae.add_requested_context("1.2.840.10008.5.1.4.1.1.2")  # Enhanced CT Image Storage
    # ae.add_requested_context(StudyRootQueryRetrieveInformationModelFind)
    assoc = ae.associate(remote_address, remote_port, ae_title="ORTHANC")
    assoc.connection_timeout = None

    print(dcm)

    if assoc.is_established:
        # Envia o arquivo DICOM
        status = assoc.send_c_store(dcm)
        print(status)

        # Fecha a associação
        assoc.release()
    else:
        print("Falha ao estabelecer a associação com o Orthanc")
