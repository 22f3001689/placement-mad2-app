"""migrate application status vocabulary

Revision ID: e3ce95e7423a
Revises: 6e172a353b32
Create Date: 2026-08-08 12:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "e3ce95e7423a"
down_revision = "6e172a353b32"
branch_labels = None
depends_on = None


def upgrade():
    # Data-only change: no column/type change, only the valid values shift
    # (waiting -> interview, selected -> offer), per Milestone 6's status
    # vocabulary (see specs/006-application-history-status/research.md).
    op.execute("UPDATE application SET status = 'interview' WHERE status = 'waiting'")
    op.execute("UPDATE application SET status = 'offer' WHERE status = 'selected'")


def downgrade():
    op.execute("UPDATE application SET status = 'waiting' WHERE status = 'interview'")
    op.execute("UPDATE application SET status = 'selected' WHERE status = 'offer'")
