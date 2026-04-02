"""
銷售儀表板模組套件
"""

from .data_processor import (
    DataProcessor,
    DataValidator,
    DataCleaner,
    KPICalculator,
    GROUP_MAPPING,
    DLR_MAPPING
)

from .google_drive_sync import (
    GoogleDriveSync,
    setup_google_credentials,
    clear_google_token
)

from .ui_styles import (
    apply_theme,
    get_metric_card_html,
    get_progress_bar_html,
    get_alert_html,
    format_currency,
    format_percentage,
    format_number,
    COLORS,
    FONTS
)

from .export_utils import (
    ExcelExporter,
    ChartGenerator,
    ImageExporter,
    ReportGenerator
)

from .ai_insights import (
    AIInsightsGenerator,
    InsightFormatter
)

from .advanced_analytics import (
    AdvancedAnalytics
)

__all__ = [
    'DataProcessor',
    'DataValidator',
    'DataCleaner',
    'KPICalculator',
    'GoogleDriveSync',
    'apply_theme',
    'get_metric_card_html',
    'get_progress_bar_html',
    'get_alert_html',
    'ExcelExporter',
    'ChartGenerator',
    'ImageExporter',
    'ReportGenerator',
    'AIInsightsGenerator',
    'InsightFormatter',
    'AdvancedAnalytics',
    'GROUP_MAPPING',
    'DLR_MAPPING',
    'COLORS',
    'FONTS'
]
