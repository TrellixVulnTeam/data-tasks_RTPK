'''
Download last versions of AM and send them to envinorma-web
'''


def _set_environment_variables() -> None:
    # To keep above OVH import to ensure env vars are set correctly
    from ..common.config import PSQL_DSN  # noqa: F401


_set_environment_variables()

import argparse  # noqa: E402

from typing_extensions import Literal  # noqa: E402

from tasks.data_build.build import from_georisques, from_s3ic  # noqa: E402
from tasks.data_build.build.build_am_repository import generate_am_repository  # noqa: F401,  E402
from tasks.data_build.build.build_ams import generate_ams  # noqa: E402
from tasks.data_build.build.build_aps import dump_ap_datasets  # noqa: E402
from tasks.data_build.build.build_georisques_ids import dump_georisques_ids  # noqa: F401, E402
from tasks.data_build.validate.check_am import check_ams  # noqa: E402
from tasks.data_build.validate.check_classements import check_classements_csv  # noqa: E402
from tasks.data_build.validate.check_documents import check_documents_csv  # noqa: E402
from tasks.data_build.validate.check_installations import check_installations_csv  # noqa: E402


def _build_from_georisques(ap_only: bool):
    if not ap_only:
        from_georisques.build_all_installations()
        from_georisques.build_all_installations_datasets()
    from_georisques.build_all_documents()
    from_georisques.build_all_documents_datasets()
    if not ap_only:
        from_georisques.build_all_classements()
        from_georisques.build_all_classements_datasets()


def _build_from_s3ic():
    from_s3ic.build_installations_csv()
    from_s3ic.build_all_installations_datasets()
    from_s3ic.build_classements_csv()
    from_s3ic.build_all_classement_datasets()
    # from_s3ic.download_georisques_documents()
    # from_s3ic.build_all_document_datasets()


def _check_installations_data():
    check_classements_csv()
    check_installations_csv()
    check_documents_csv()


_Source = Literal['s3ic', 'georisques']


def _build_installations_data(ap_only: bool, source: _Source):
    if source == 's3ic':
        _build_from_s3ic()
    elif source == 'georisques':
        _build_from_georisques(ap_only)
    else:
        raise ValueError(f'Unknown source: {source}')
    dump_ap_datasets()
    # dump_georisques_ids(filename)


def _handle_installations_data(ap_only: bool, source: _Source):
    _build_installations_data(ap_only, source)
    _check_installations_data()


def _handle_ams(with_repository: bool) -> None:
    generate_ams()
    if with_repository:
        generate_am_repository()
    check_ams()


def run(
    source: _Source = 'georisques',
    with_repository: bool = False,
    handle_ams: bool = False,
    handle_installations_data: bool = False,
    handle_aps: bool = False,
) -> None:
    if handle_ams:
        _handle_ams(with_repository)
    if handle_installations_data:
        _handle_installations_data(False, source)
    if handle_aps:
        _handle_installations_data(handle_aps, source)


def cli():
    parser = argparse.ArgumentParser(description='Build data for envinorma-web')
    parser.add_argument('--source', type=str, default='georisques', help='Source of data (georisques or s3ic)')
    parser.add_argument('--with-repository', action='store_true', help='Generate AM repository')
    parser.add_argument('--handle-ams', action='store_true', help='Generate AMs')
    parser.add_argument('--handle-installations-data', action='store_true', help='Generate installation data')
    parser.add_argument('--handle-aps', action='store_true', help='Generate APs')
    args = parser.parse_args()

    run(args.source, args.with_repository, args.handle_ams, args.handle_installations_data, args.handle_aps)


if __name__ == '__main__':
    cli()
