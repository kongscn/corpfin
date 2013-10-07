from sqlalchemy import create_engine, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.session import object_session

from corpfin.util.config import ENGINE

engine = create_engine(ENGINE)
Base = declarative_base()
Base.metadata.reflect(engine)
Session = sessionmaker(bind=engine)
default_session = Session()

class Base(Base):
    __abstract__ = True

    @classmethod
    def qobjects(cls, qsession=None):
        qsession = (qsession or default_session)
        return qsession.query(cls)


class SectorStandard(Base):
    __table__ = Base.metadata.tables['sector_standard']

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__,
                               self.abbr, self.name)


class Sector(Base):
    __table__ = Base.metadata.tables['sector']
    children = relationship("Sector", cascade="all, delete-orphan", order_by='Sector.id',
                            backref=backref('parent', remote_side=__table__.c.id))
    standard = relationship(SectorStandard, backref=backref('sectors', order_by='Sector.id'))

    def __repr__(self):
        return '<%s %s %s %s>' % (self.__class__.__name__,
                                  self.id, self.code, self.name)


class Country(Base):
    __table__ = Base.metadata.tables['country']

    def __repr__(self):
        return '<%s %s %s %s>' % (self.__class__.__name__,
                                  self.id, self.iso, self.name_en)


class District(Base):
    __table__ = Base.metadata.tables['district']
    children = relationship("District", order_by='District.name',
                            backref=backref('parent', remote_side=__table__.c.id))

    def __repr__(self):
        return '<%s %s %s %s>' % (self.__class__.__name__,
                                  self.id, self.name, self.zipcode)


class Company(Base):
    __table__ = Base.metadata.tables['company']
    secondary = Base.metadata.tables['company_districts']
    country = relationship("Country", backref=backref('companies', order_by='Company.name'))
    districts = relationship("District", secondary=Base.metadata.tables['company_districts'],
                             order_by='District.id',
                             backref=backref('companies', order_by='Company.name'))

    #state = relationship("District", secondary=secondary,
    #                     primaryjoin=__table__.c.id == secondary.c.company_id,
    #                     secondaryjoin=and_(secondary.c.district_id == District.id,
    #                                        District.parent_id == None)
    #)
    #city = relationship("District", secondary=secondary,
    #                    primaryjoin=__table__.c.id == secondary.c.company_id,
    #                    secondaryjoin=and_(secondary.c.district_id == District.id,
    #                                       District.parent_id != None)
    #)
    def _get_state(self):
        q = object_session(self).query(District)
        q = q.join(self.secondary).join(Company)
        q = q.filter(Company.id==self.id).filter(District.parent_id==None)
        return q.one()

    state = property(_get_state)

    def _get_city(self):
        q = object_session(self).query(District)
        q = q.join(self.secondary).join(Company)
        q = q.filter(Company.id==self.id).filter(District.parent_id!=None)
        cities = q.all()
        if len(cities) > 0:
            return cities[-1]
        else:
            return 'City unknown'

    city = property(_get_city)

    def __repr__(self):
        return '<%s %s %s %s>' % (self.__class__.__name__,
                                  self.id, self.symbol, self.name)


class Exchange(Base):
    __table__ = Base.metadata.tables['exchange']
    children = relationship("Exchange", backref=backref('parent', remote_side=__table__.c.id))

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__,
                               self.symbol, self.name)

class Product(Base):
    __table__ = Base.metadata.tables['product']
    company = relationship("Company", backref='products')
    exchanges = relationship("Exchange", secondary=Base.metadata.tables['product_exchanges'],
                             backref='products')
    sectors = relationship("Sector", secondary=Base.metadata.tables['product_sectors'],
                           backref='products')

    def __repr__(self):
        return '<%s %s %s %s>' % (self.__class__.__name__,
                                  self.id, self.symbol, self.company.name)

class Index(Base):
    __table__ = Base.metadata.tables['index']
    products = relationship("Product", secondary=Base.metadata.tables['index_products'],
                            backref='indexes')

    def __repr__(self):
        return '<%s %s %s %s>' % (self.__class__.__name__,
                                   self.id, self.symbol, self.name)

class OHLCBase(Base):
    __abstract__ = True
    columns = ['date', 'open', 'high', 'low', 'close', 'adj_close', 'volume']
    def values(self, columns=None):
        if columns is None: columns = self.columns
        return [self.__getattribute__(key) for key in columns]
    def dict(self, columns=None):
        if columns is None: columns = self.columns
        return {key: self.__getattribute__(key) for key in columns}
    # product = relationship('Product')
    
    def _get_symbol(self):
        return self.product.symbol
    symbol = property(_get_symbol)
    
    def __repr__(self):
        return '<%s %s %s %s %s %s %s %s>' % (self.__class__.__name__, self.date,
                                              self.open, self.high, self.low, self.close,
                                              self.adj_close, self.volume)


class OHLCDaily(OHLCBase):
    __table__ = Base.metadata.tables['ohlc_d']
    product = relationship('Product', backref=backref('ohlc_d', cascade="all, delete-orphan"))


class OHLCWeekly(OHLCBase):
    __table__ = Base.metadata.tables['ohlc_w']
    product = relationship('Product', backref=backref('ohld_w', cascade="all, delete-orphan"))


class OHLCMonthly(OHLCBase):
    __table__ = Base.metadata.tables['ohlc_m']
    product = relationship('Product', backref=backref('ohld_m', cascade="all, delete-orphan"))

