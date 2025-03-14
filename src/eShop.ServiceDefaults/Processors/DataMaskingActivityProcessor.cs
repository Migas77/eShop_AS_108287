using OpenTelemetry;
using System.Diagnostics;
using Newtonsoft.Json;
using Microsoft.Extensions.Logging;

namespace eShop.ServiceDefaults.Processors;

public class DataMaskingActivityProcessor : BaseProcessor<Activity>
{
    private readonly ILogger<DataMaskingActivityProcessor> _logger;

    public DataMaskingActivityProcessor(ILogger<DataMaskingActivityProcessor> logger)
    {
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }
    
    public override void OnEnd(Activity activity)
    {
        if (activity == null) return;

        var tags = activity.Tags.ToList();

        foreach (var tag in tags)
        {
            if (tag.Value == null) continue;

            if (tag.Value.StartsWith("{") && tag.Value.EndsWith("}")) {
                // Process Nested Dictionary Tags (Events - RabbitMQ Publish/Receive mostly)
                try {
                    var dictionary = JsonConvert.DeserializeObject<Dictionary<string, object>>(tag.Value);
                    if (dictionary != null)
                    {
                        foreach (var nestedTag in dictionary) {
                            if (nestedTag.Value == null || nestedTag.Value is not string value) continue;
                            var maskedValue = DataMasking.Mask(new KeyValuePair<string, string>(nestedTag.Key, value));
                            if (maskedValue != null) {
                                dictionary[nestedTag.Key] = maskedValue;
                            }
                        }
                        activity.SetTag(tag.Key, JsonConvert.SerializeObject(dictionary));
                    }
                } catch (JsonException ex) {
                    _logger.LogError(ex, "Error deserializing dictionary from tag value");
                }
            } else {
                // Process Simple Activity Tags
                var maskedValue = DataMasking.Mask(new KeyValuePair<string, string>(tag.Key, tag.Value));
                if (maskedValue != null) {
                    activity.SetTag(tag.Key, maskedValue);
                }
            }
        }
    }

    
}
