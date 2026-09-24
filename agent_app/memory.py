from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker
)


DATABASE_URL = "sqlite:///memory.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


Base = declarative_base()


SessionLocal = sessionmaker(
    bind=engine
)


class Conversation(Base):

    __tablename__ = "conversations"

    id = Column(
        Integer,
        primary_key=True
    )

    session_id = Column(
        String,
        index=True
    )

    user_message = Column(
        Text
    )

    assistant_message = Column(
        Text
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


Base.metadata.create_all(engine)


def save_message(
    session_id: str,
    user_message: str,
    assistant_message: str
):

    db = SessionLocal()

    conversation = Conversation(
        session_id=session_id,
        user_message=user_message,
        assistant_message=assistant_message
    )

    db.add(conversation)

    db.commit()

    db.close()


def get_history(
    session_id: str,
    limit: int = 10
):

    db = SessionLocal()

    rows = (
        db.query(Conversation)
        .filter(
            Conversation.session_id == session_id
        )
        .order_by(
            Conversation.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    db.close()

    rows.reverse()

    return rows