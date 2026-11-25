"""Preserve questionnaire options and next question for resuming sessions."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "c4a812f6d930"
down_revision = "88b046f9e2be"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "questionnaire_sessions",
        sa.Column("next_question", postgresql.JSONB(none_as_null=True), nullable=True),
    )
    op.add_column(
        "questionnaire_sessions",
        sa.Column(
            "questionnaire_options", postgresql.JSONB(),
            nullable=False, server_default=sa.text("'{}'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("questionnaire_sessions", "questionnaire_options")
    op.drop_column("questionnaire_sessions", "next_question")
