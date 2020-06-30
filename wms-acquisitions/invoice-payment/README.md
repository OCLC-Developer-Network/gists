**Start with an invoice in READY_TO_PAY status:**

GET https://128807.share.worldcat.org/acquisitions/invoice/data/INV-2012-2

Result:
```xml
<?xml version="1.0" encoding="UTF-8"?><entry xmlns="http://www.w3.org/2005/Atom">
  <title type="text">INV-2012-2</title>
  <id>https://acq.sd00.worldcat.org/acquisitions/invoice/data/INV-2012-2</id>
  <published>2012-06-28T18:33:13.000Z</published>
  <updated>2020-06-30T18:24:41.826Z</updated>
  <content type="application/xml">
    <ns7:Invoice xmlns:ns7="http://purl.org/oclc/ontology/acquisitions/" xmlns="http://worldcat.org/xmlschemas/acquisitions/PurchaseOrder" xmlns:ns2="http://worldcat.org/xmlschemas/common-types/Identity" xmlns:ns4="http://worldcat.org/xmlschemas/acquisitions/Resource" xmlns:ns3="http://worldcat.org/xmlschemas/acquisitions/PurchaseOrderItem" xmlns:ns6="http://worldcat.org/xmlschemas/acquisitions/CustomField" xmlns:ns5="http://worldcat.org/xmlschemas/acquisitions/CopyConfig" xmlns:ns8="http://worldcat.org/xmlschemas/acquisitions/Copy" xmlns:ns13="http://www.w3.org/2004/02/skos/core#" xmlns:ns9="http://worldcat.org/xmlschemas/acquisitions/CopyReceipt" xmlns:ns12="http://schema.org/" xmlns:ns11="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:ns10="http://worldcat.org/xmlschemas/acquisitions/PurchaseOrderSubmission" xmlns:ns14="http://worldcat.org/xmlschemas/response" ns11:about="https://acq.sd00.worldcat.org/acquisitions/invoice/data/INV-2012-2">
      <ns12:name>INV-2012-2</ns12:name>
      <ns12:dateCreated>2012-06-28T14:33:13.000-04:00</ns12:dateCreated>
      <ns12:dateModified>2020-06-30T14:24:41.826-04:00</ns12:dateModified>
      <ns7:id>https://acq.sd00.worldcat.org/acquisitions/invoice/data/INV-2012-2</ns7:id>
      <ns7:taxCalculationMethod>
        <ns7:TaxCalculationMethod>EXCLUDE_ADDITIONAL_COSTS</ns7:TaxCalculationMethod>
      </ns7:taxCalculationMethod>
      <ns7:itemCount>4</ns7:itemCount>
      <ns7:grandTotal>
        <ns12:PriceSpecification>
          <ns12:price>61.07</ns12:price>
          <ns12:priceCurrency>USD</ns12:priceCurrency>
        </ns12:PriceSpecification>
      </ns7:grandTotal>
      <ns7:totalDiscount>
        <ns12:PriceSpecification>
          <ns12:price>0.00</ns12:price>
          <ns12:priceCurrency>USD</ns12:priceCurrency>
        </ns12:PriceSpecification>
      </ns7:totalDiscount>
      <ns7:totalTax>
        <ns12:PriceSpecification>
          <ns12:price>0.00</ns12:price>
          <ns12:priceCurrency>USD</ns12:priceCurrency>
        </ns12:PriceSpecification>
      </ns7:totalTax>
      <ns7:totalServiceCharge>
        <ns12:PriceSpecification>
          <ns12:price>0.00</ns12:price>
          <ns12:priceCurrency>USD</ns12:priceCurrency>
        </ns12:PriceSpecification>
      </ns7:totalServiceCharge>
      <ns7:totalShippingCharge>
        <ns12:PriceSpecification>
          <ns12:price>0.00</ns12:price>
          <ns12:priceCurrency>USD</ns12:priceCurrency>
        </ns12:PriceSpecification>
      </ns7:totalShippingCharge>
      <ns7:comment/>
      <ns7:currency>USD</ns7:currency>
      <ns7:exchangeRate>1.0000000000</ns7:exchangeRate>
      <ns7:invoiceNumber>INV-2012-2</ns7:invoiceNumber>
      <ns7:invoiceStatus>
        <ns7:InvoiceStatus>READY_TO_PAY</ns7:InvoiceStatus>
      </ns7:invoiceStatus>
      <ns7:vendorInvoiceNumber>KAC-12345</ns7:vendorInvoiceNumber>
      <ns7:vendorInvoiceDate>2012-06-28</ns7:vendorInvoiceDate>
      <ns7:receivedFrom>
        <ns7:Vendor ns11:resource="https://vic.sd00.worldcat.org/vendors/c796db47-deed-4716-abda-fb0815c09ddf">
          <ns12:name>Amazon</ns12:name>
          <ns7:id>c796db47-deed-4716-abda-fb0815c09ddf</ns7:id>
        </ns7:Vendor>
      </ns7:receivedFrom>
      <ns7:hasLineItems ns11:resource="https://acq.sd00.worldcat.org/acquisitions/invoiceitem/search?q=invoiceNumber:INV-2012-2"/>
      <ns7:paymentMethod ns11:resource="http://purl.org/goodrelations/v1#ByInvoice"/>
    </ns7:Invoice>
  </content>
</entry>
```

**Next, pay the invoice using the the /pay endpoint:**

PUT https://128807.share.worldcat.org/acquisitions/invoice/pay/INV-2012-2

The invoice status field is updated to PAID:

```xml
<ns7:InvoiceStatus>PAID</ns7:InvoiceStatus>
```

The system also sets the datePaid field:

```xml
<ns7:datePaid>2020-06-30T14:41:33.028-04:00</ns7:datePaid>
```

The datePaid field cannot be set by the API.

**A new field called userPaidDate is now available so that you can set a paid date independent of the system-generated datePaid field.** If not specified, the userPaidDate field defaults to the current date. This is what happens when you use the /pay endpoint, which does not take a request body. In the above example, you would see:

```xml
<ns7:userPaidDate>2020-06-30</ns7:userPaidDate>
```

In order to update the userPaidDate field, use the /data endpoint:

PUT https://128807.share.worldcat.org/acquisitions/invoice/data/INV-2012-2

Request body:
```xml
<?xml version="1.0" encoding="UTF-8"?><entry xmlns="http://www.w3.org/2005/Atom">
  <title type="text">INV-2012-2</title>
  <id>https://acq.sd00.worldcat.org/acquisitions/invoice/data/INV-2012-2</id>
  <published>2012-06-28T18:33:13.000Z</published>
  <updated>2020-06-30T18:41:33.100Z</updated>
  <content type="application/xml">
    <ns7:Invoice xmlns:ns7="http://purl.org/oclc/ontology/acquisitions/" xmlns="http://worldcat.org/xmlschemas/acquisitions/PurchaseOrder" xmlns:ns2="http://worldcat.org/xmlschemas/common-types/Identity" xmlns:ns4="http://worldcat.org/xmlschemas/acquisitions/Resource" xmlns:ns3="http://worldcat.org/xmlschemas/acquisitions/PurchaseOrderItem" xmlns:ns6="http://worldcat.org/xmlschemas/acquisitions/CustomField" xmlns:ns5="http://worldcat.org/xmlschemas/acquisitions/CopyConfig" xmlns:ns8="http://worldcat.org/xmlschemas/acquisitions/Copy" xmlns:ns13="http://www.w3.org/2004/02/skos/core#" xmlns:ns9="http://worldcat.org/xmlschemas/acquisitions/CopyReceipt" xmlns:ns12="http://schema.org/" xmlns:ns11="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:ns10="http://worldcat.org/xmlschemas/acquisitions/PurchaseOrderSubmission" xmlns:ns14="http://worldcat.org/xmlschemas/response" ns11:about="https://acq.sd00.worldcat.org/acquisitions/invoice/data/INV-2012-2">
      <ns12:name>INV-2012-2</ns12:name>
      <ns12:dateCreated>2012-06-28T14:33:13.000-04:00</ns12:dateCreated>
      <ns12:dateModified>2020-06-30T14:41:33.100-04:00</ns12:dateModified>
      <ns7:id>https://acq.sd00.worldcat.org/acquisitions/invoice/data/INV-2012-2</ns7:id>
      <ns7:taxCalculationMethod>
        <ns7:TaxCalculationMethod>EXCLUDE_ADDITIONAL_COSTS</ns7:TaxCalculationMethod>
      </ns7:taxCalculationMethod>
      <ns7:itemCount>4</ns7:itemCount>
      <ns7:grandTotal>
        <ns12:PriceSpecification>
          <ns12:price>61.07</ns12:price>
          <ns12:priceCurrency>USD</ns12:priceCurrency>
        </ns12:PriceSpecification>
      </ns7:grandTotal>
      <ns7:totalDiscount>
        <ns12:PriceSpecification>
          <ns12:price>0.00</ns12:price>
          <ns12:priceCurrency>USD</ns12:priceCurrency>
        </ns12:PriceSpecification>
      </ns7:totalDiscount>
      <ns7:totalTax>
        <ns12:PriceSpecification>
          <ns12:price>0.00</ns12:price>
          <ns12:priceCurrency>USD</ns12:priceCurrency>
        </ns12:PriceSpecification>
      </ns7:totalTax>
      <ns7:totalServiceCharge>
        <ns12:PriceSpecification>
          <ns12:price>0.00</ns12:price>
          <ns12:priceCurrency>USD</ns12:priceCurrency>
        </ns12:PriceSpecification>
      </ns7:totalServiceCharge>
      <ns7:totalShippingCharge>
        <ns12:PriceSpecification>
          <ns12:price>0.00</ns12:price>
          <ns12:priceCurrency>USD</ns12:priceCurrency>
        </ns12:PriceSpecification>
      </ns7:totalShippingCharge>
      <ns7:comment/>
      <ns7:currency>USD</ns7:currency>
      <ns7:exchangeRate>1.0000000000</ns7:exchangeRate>
      <ns7:invoiceNumber>INV-2012-2</ns7:invoiceNumber>
      <ns7:invoiceStatus>
        <ns7:InvoiceStatus>PAID</ns7:InvoiceStatus>
      </ns7:invoiceStatus>
      <ns7:vendorInvoiceNumber>KAC-12345</ns7:vendorInvoiceNumber>
      <ns7:vendorInvoiceDate>2012-06-28</ns7:vendorInvoiceDate>
      <ns7:receivedFrom>
        <ns7:Vendor ns11:resource="https://vic.sd00.worldcat.org/vendors/c796db47-deed-4716-abda-fb0815c09ddf">
          <ns12:name>Amazon</ns12:name>
          <ns7:id>c796db47-deed-4716-abda-fb0815c09ddf</ns7:id>
        </ns7:Vendor>
      </ns7:receivedFrom>
      <ns7:datePaid>2020-06-30T14:41:33.028-04:00</ns7:datePaid>
      <ns7:hasLineItems ns11:resource="https://acq.sd00.worldcat.org/acquisitions/invoiceitem/search?q=invoiceNumber:INV-2012-2"/>
      <ns7:paymentMethod ns11:resource="http://purl.org/goodrelations/v1#ByInvoice"/>
      <ns7:userPaidDate>2020-06-01</ns7:userPaidDate>
    </ns7:Invoice>
  </content>
</entry>
```

**"Un-paying" the invoice will remove any data from the datePaid and userPaidDate fields.** For example, if I re-open this invoice using the /open endpoint:

PUT https://128807.share.worldcat.org/acquisitions/invoice/open/INV-2012-2

I get this response:

```xml
<?xml version="1.0" encoding="UTF-8"?><entry xmlns="http://www.w3.org/2005/Atom">
  <title type="text">INV-2012-2</title>
  <id>https://acq.sd00.worldcat.org/acquisitions/invoice/data/INV-2012-2</id>
  <published>2012-06-28T18:33:13.000Z</published>
  <updated>2020-06-30T19:15:13.750Z</updated>
  <content type="application/xml">
    <ns7:Invoice xmlns:ns7="http://purl.org/oclc/ontology/acquisitions/" xmlns="http://worldcat.org/xmlschemas/acquisitions/PurchaseOrder" xmlns:ns2="http://worldcat.org/xmlschemas/common-types/Identity" xmlns:ns4="http://worldcat.org/xmlschemas/acquisitions/Resource" xmlns:ns3="http://worldcat.org/xmlschemas/acquisitions/PurchaseOrderItem" xmlns:ns6="http://worldcat.org/xmlschemas/acquisitions/CustomField" xmlns:ns5="http://worldcat.org/xmlschemas/acquisitions/CopyConfig" xmlns:ns8="http://worldcat.org/xmlschemas/acquisitions/Copy" xmlns:ns13="http://www.w3.org/2004/02/skos/core#" xmlns:ns9="http://worldcat.org/xmlschemas/acquisitions/CopyReceipt" xmlns:ns12="http://schema.org/" xmlns:ns11="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:ns10="http://worldcat.org/xmlschemas/acquisitions/PurchaseOrderSubmission" xmlns:ns14="http://worldcat.org/xmlschemas/response" ns11:about="https://acq.sd00.worldcat.org/acquisitions/invoice/data/INV-2012-2">
      <ns12:name>INV-2012-2</ns12:name>
      <ns12:dateCreated>2012-06-28T14:33:13.000-04:00</ns12:dateCreated>
      <ns12:dateModified>2020-06-30T15:15:13.750-04:00</ns12:dateModified>
      <ns7:id>https://acq.sd00.worldcat.org/acquisitions/invoice/data/INV-2012-2</ns7:id>
      <ns7:taxCalculationMethod>
        <ns7:TaxCalculationMethod>EXCLUDE_ADDITIONAL_COSTS</ns7:TaxCalculationMethod>
      </ns7:taxCalculationMethod>
      <ns7:itemCount>4</ns7:itemCount>
      <ns7:grandTotal>
        <ns12:PriceSpecification>
          <ns12:price>61.07</ns12:price>
          <ns12:priceCurrency>USD</ns12:priceCurrency>
        </ns12:PriceSpecification>
      </ns7:grandTotal>
      <ns7:totalDiscount>
        <ns12:PriceSpecification>
          <ns12:price>0.00</ns12:price>
          <ns12:priceCurrency>USD</ns12:priceCurrency>
        </ns12:PriceSpecification>
      </ns7:totalDiscount>
      <ns7:totalTax>
        <ns12:PriceSpecification>
          <ns12:price>0.00</ns12:price>
          <ns12:priceCurrency>USD</ns12:priceCurrency>
        </ns12:PriceSpecification>
      </ns7:totalTax>
      <ns7:totalServiceCharge>
        <ns12:PriceSpecification>
          <ns12:price>0.00</ns12:price>
          <ns12:priceCurrency>USD</ns12:priceCurrency>
        </ns12:PriceSpecification>
      </ns7:totalServiceCharge>
      <ns7:totalShippingCharge>
        <ns12:PriceSpecification>
          <ns12:price>0.00</ns12:price>
          <ns12:priceCurrency>USD</ns12:priceCurrency>
        </ns12:PriceSpecification>
      </ns7:totalShippingCharge>
      <ns7:comment/>
      <ns7:currency>USD</ns7:currency>
      <ns7:exchangeRate>1.0000000000</ns7:exchangeRate>
      <ns7:invoiceNumber>INV-2012-2</ns7:invoiceNumber>
      <ns7:invoiceStatus>
        <ns7:InvoiceStatus>OPEN</ns7:InvoiceStatus>
      </ns7:invoiceStatus>
      <ns7:vendorInvoiceNumber>KAC-12345</ns7:vendorInvoiceNumber>
      <ns7:vendorInvoiceDate>2012-06-28</ns7:vendorInvoiceDate>
      <ns7:receivedFrom>
        <ns7:Vendor ns11:resource="https://vic.sd00.worldcat.org/vendors/c796db47-deed-4716-abda-fb0815c09ddf">
          <ns12:name>Amazon</ns12:name>
          <ns7:id>c796db47-deed-4716-abda-fb0815c09ddf</ns7:id>
        </ns7:Vendor>
      </ns7:receivedFrom>
      <ns7:hasLineItems ns11:resource="https://acq.sd00.worldcat.org/acquisitions/invoiceitem/search?q=invoiceNumber:INV-2012-2"/>
      <ns7:paymentMethod ns11:resource="http://purl.org/goodrelations/v1#ByInvoice"/>
    </ns7:Invoice>
  </content>
</entry>
```
