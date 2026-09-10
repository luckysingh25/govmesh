import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from app.application.intelligence_service import IntelligenceService

@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

@pytest.fixture(scope="module")
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(engine, tables):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_intelligence_schema_ingestion(db_session):
    service = IntelligenceService()
    v1_schema = {
        "properties": {
            "ownerName": {"type": "string"},
            "propertyId": {"type": "string"}
        }
    }
    
    schema = service.ingest_schema(db_session, "TestSystem", v1_schema)
    assert schema.id is not None
    assert schema.version == 1
    assert len(schema.fields) == 2
    
    # Check that ownerName normalized mapping suggestion is created
    suggestions = [f for f in schema.fields if f.field_name == "ownerName"][0].mappings
    assert len(suggestions) > 0
    assert suggestions[0].target_field == "property.owner_name"

def test_intelligence_impact_analysis(db_session):
    service = IntelligenceService()
    # Ingest V2 with a renamed field
    v2_schema = {
        "properties": {
            "propertyOwnerName": {"type": "string"},
            "propertyId": {"type": "string"}
        }
    }
    
    schema_v2 = service.ingest_schema(db_session, "TestSystem", v2_schema)
    assert schema_v2.version == 2
    
    from app.models.intelligence import ImpactAnalysis
    impact = db_session.query(ImpactAnalysis).filter_by(new_version=2).first()
    assert impact is not None
    assert "ownerName" in [r["old"] for r in impact.analysis_result["changes"]["renamed"]]
