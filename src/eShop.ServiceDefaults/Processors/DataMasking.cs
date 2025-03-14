namespace eShop.ServiceDefaults.Processors;

internal static class DataMasking
{
    private static readonly Dictionary<string, int> SensitiveKeys = new()
    {
        // Comparison bellow is case insensitive
        { "userId", 33 },
        { "buyerId", 33 },
        { "subjectId", 33 },
        { "BuyerIdentityGuid", 33 },
        { "userName" , 128 },
        { "buyerName" , 128 },
        { "CardNumber",  13 },
        { "CardHolderName", 128 }
    };

    internal static string? Mask(KeyValuePair<string, string> tag) {
        var matchingKey = SensitiveKeys.Keys.FirstOrDefault(k => tag.Key.Contains(k, StringComparison.OrdinalIgnoreCase));

        if (matchingKey != default && tag.Value?.ToString() is string strValue)
        {
            var maskLength = Math.Min(SensitiveKeys[matchingKey], strValue.Length);
            var unMaskedLength = strValue.Length - maskLength;
            var unmaskedPrefix = unMaskedLength > 0 ? strValue[..unMaskedLength] : "";
            var maskedSuffix = new string('*', maskLength);
            return unmaskedPrefix + maskedSuffix;
        }
        return null;
    }
}