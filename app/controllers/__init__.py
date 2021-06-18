# flake8: noqa F401
from .csx_parser import CSXParser
from .union_parser import UnionParser
from .kansas_city_southern_parser import KansasCitySouthernParser
from .canadian_national_parser import CanadianNationalParser
from .canadian_pacific_parser import CanadianPacificParser
from .bnsf_parser import BNSFParser
from .norfolk_southern_parser import NorfolkSouthernParser


def data_scrap():
    from app.models import Passed
    from config import BaseConfig as conf
    from app.logger import log

    for year in range(conf.BEGIN_YEAR, conf.CURRENT_YEAR + 1):
        log(log.INFO, "=================== Year: %d", year)
        finish_week = conf.CURRENT_WEEK if year == conf.CURRENT_YEAR else 53
        for week in range(1, finish_week + 1):
            log(log.INFO, "=================== Week %d of %d", week, year)
            COMPANIES = {
                CSXParser: "CSX",
                UnionParser: "Union Parser",
                NorfolkSouthernParser: "Norfolk Southern",
                KansasCitySouthernParser: "Kansas City Southern Parser",
                CanadianNationalParser: "Canadian National Parser",
                BNSFParser: "BNSF Parser",
                CanadianPacificParser: "CanadianPacificParser",
            }
            for Parser, company_name in COMPANIES.items():
                p = (
                    Passed.query.filter(Passed.company_name == company_name)
                    .filter(Passed.year == year)
                    .filter(Passed.week == week)
                    .first()
                )
                if p:
                    log(log.INFO, "Already done for [%s]", company_name)
                    continue
                log(log.INFO, "----------- Start parser %s", company_name)
                parser = Parser(year_no=year, week_no=week)
                file = parser.get_file()
                if not file:
                    log(
                        log.WARNING,
                        "Cannot get data file. FOR YEAR:%s WEEK:%s",
                        year,
                        week,
                    )
                    if conf.CURRENT_YEAR == year and (
                        conf.CURRENT_WEEK == week or conf.CURRENT_WEEK == week + 1
                    ):
                        continue
                else:
                    log(log.INFO, "Got file %s", company_name)
                    parser.parse_data()
                    log(log.INFO, "End parser data %s", company_name)
                Passed(company_name=company_name, year=year, week=week).save()
