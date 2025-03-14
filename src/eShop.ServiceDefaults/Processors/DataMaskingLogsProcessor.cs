using OpenTelemetry;
using Microsoft.Extensions.Logging;
using OpenTelemetry.Logs;

namespace eShop.ServiceDefaults.Processors;

public class DataMaskingLogsProcessor : BaseProcessor<LogRecord>
{
    private readonly ILogger<DataMaskingLogsProcessor> _logger;

    public DataMaskingLogsProcessor(ILogger<DataMaskingLogsProcessor> logger)
    {
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public override void OnEnd(LogRecord record)
    {
        if (record == null || record.FormattedMessage==null) return;
        
        // Process the body content
        record.FormattedMessage = DataMasking.MaskPairInString(record.FormattedMessage);
        
    }
}