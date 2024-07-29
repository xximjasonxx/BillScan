
using System.Text;
using Azure.Storage.Blobs;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json.Linq;

var config = new ConfigurationBuilder()
    .AddUserSecrets<Config>()
    .Build();

Console.Write("Please specify a Congress number (<=118): ");
var congressNumber = Console.ReadLine();
Console.WriteLine();

Console.Write("Please specify a bill number to start at (eg. 1): ");
var minBillNumber = Console.ReadLine();
Console.WriteLine();

Console.Write("Please specify a bill number to end at (eg. 100): ");
var maxBillNumber = Console.ReadLine();
Console.WriteLine();

var client = new HttpClient() { BaseAddress = new Uri("https://www.govtrack.us") };
var blobServiceClient = new BlobServiceClient(config["StorageAccountConnectionString"]);
var jsonContainer = blobServiceClient.GetBlobContainerClient("bills-json");
var pdfContainer = blobServiceClient.GetBlobContainerClient("bills-pdf");

HttpResponseMessage response = null;
for (int billNumber = int.Parse(minBillNumber); billNumber <= int.Parse(maxBillNumber); billNumber++)
{
    Console.Write($"Accessing bill HR{billNumber}...");
    response = await client.GetAsync($"/congress/bills/{congressNumber}/hr{billNumber}.json");
    if (response.IsSuccessStatusCode)
    {
        Console.Write("done.");
        Console.WriteLine();
        Console.Write($"Saving bill HR{billNumber} details...");
        var json = await response.Content.ReadAsStringAsync();
        var jsonBlob = jsonContainer.GetBlobClient($"{congressNumber}hr{billNumber}.json");
        await jsonBlob.UploadAsync(new MemoryStream(Encoding.UTF8.GetBytes(json)), true);
        Console.Write("done.");
        Console.WriteLine();

        Console.Write($"Downloading bill HR{billNumber} PDF...");
        var billDetailJson = JObject.Parse(json);
        var billPdfUrl = billDetailJson["text_info"]["gpo_pdf_url"].Value<string>();
        var pdfResponse = await client.GetAsync(billPdfUrl);
        var pdfBlob = pdfContainer.GetBlobClient($"{congressNumber}hr{billNumber}.pdf");
        await pdfBlob.UploadAsync(pdfResponse.Content.ReadAsStream(), true);
        Console.Write("done.");
    }
    else
    {
        Console.Write("not found.");
    }

    Console.WriteLine();
    Console.WriteLine();
}