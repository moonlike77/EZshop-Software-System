

# Requirements Document - EZShop

Date: 24/10/2025

Version: 1.0.0

| Version number | Change |
| :------------: | :----: |
|                |        |

# Contents

- [Requirements Document - EzShop](#requirements-document)
- [Contents](#contents)
- [Informal description](#informal-description)
- [Business model](#business-model)
- [Stakeholders](#stakeholders)
- [Context Diagram and interfaces](#context-diagram-and-interfaces)
  - [Context Diagram](#context-diagram)
  - [Interfaces](#interfaces)
- [Functional and non functional requirements](#functional-and-non-functional-requirements)
  - [Functional Requirements](#functional-requirements)
  - [Non Functional Requirements](#non-functional-requirements)
- [Table of Rights](#table-of-rights)
- [Use case diagram and use cases](#use-case-diagram-and-use-cases)
  - [Use case diagram](#use-case-diagram)
    - [Use case 1, UC1](#use-case-1-uc1)
      - [Scenario 1.1](#scenario-11)
      - [Scenario 1.2](#scenario-12)
      - [Scenario 1.x](#scenario-1x)
    - [Use case 2, UC2](#use-case-2-uc2)
    - [Use case x, UCx](#use-case-x-ucx)
- [Glossary](#glossary)
- [System Design](#system-design)
- [Hardware Software architecture](#Hardware-software-architecture)

# Informal description

Small shops require a simple application to support the owner or manager. A small shop (ex a food shop) occupies 50-200 square meters, sells 500-2000 different item types, has two or a few more cash registers. 
EZShop is a software application to:
* manage sales
* manage inventory
* manage orders to suppliers
* support accounting

In the following describe the requirements of the EZShop application. 
You are free to define the application as you deem more useful and effective for the stakeholders. 
You are also free to modify the structure of the document when needed.
The document will be evaluated considering the typical defects in requirements (omissions, ambiguities, contradictions, etc), and syntactic errors in the formalism used (UML diagrams). 
Consider that the document should be delivered to another team (unknown to you)
 which will be in charge of designing and implementing the system. The design team should be able to proceed only with the information in the document.

# Business Model

The EZShop system is designed to be a high-value, affordable, and scalable solution for small, independent retailers. The business model is centered on providing a product that directly increases the profitability and operational efficiency of the target shops (Convenience Stores, Small Grocers, Local Hardware Stores, Pet Stores, Small Bookstores/Toy Stores).

### 1\. Value Proposition

* **Increase Profitability:** Real-time inventory (FR5) prevents lost sales/overstocking. Accurate tracking ensures correct margins.  
* **Improve Operational Efficiency:** Fast sale speeds checkout. Automated inventory (FR5) and simplified ordering reduce manual work.  
* **Enable Data-Driven Decisions:** Clear reports offer immediate insights into sales, profitability, and reordering needs.  
* **Reduce Risk & Errors:** Minimizes checkout mistakes, reduces stock shrinkage, and ensures accurate sales data for compliance.

### 2\. Revenue Streams

**2.1. SaaS (Software as a Service)**

* **Recurring Fee:** Monthly/Annual payment.  
* **Tiered Plans:** Different feature levels (e.g., "Basic" \- 1 register, 500 items; "Pro" \- 5 registers, 2000 items, advanced reports).  
* **Cloud-Based:** EZShop hosts the server and database

**2.2. Perpetual License** 

* **Payment Structure:** A single, upfront payment covers the software license (One-Time Fee).  
* **Deployment:** The software, including the server and database, is deployed locally on the customer's premises (Local Deployment) and is downloadable on smartphones, laptops, tablets and PCs for online shopping.  
* **Support & Updates:** Customers have the option to purchase a recurring annual fee for maintenance, which provides access to software updates and dedicated technical support (Optional Maintenance Fee).

### 3\. Distribution Channels:

* **Direct Sales:** EZShop's dedicated website will offer SaaS and perpetual licenses, allowing owners to learn about pricing and sign up directly.  
* **Reseller Partnerships:** Partner with POS hardware vendors (scanners, printers, etc.) to bundle EZShop as a complete system.  
* **IT Support Resellers:** Partner with local IT support firms that service small businesses to resell and install the EZShop system for their clients.

# Stakeholders

| Stakeholder name | Description |
| :----: | :---- |
| **Shop Owner** | The Shop Owner has full administrative access and oversees all business operations such as staff management, pricing, inventory, profitability and supplier relationships. They prioritize an affordable, reliable system with clear reports (sales, stock, profit) for effective business management. |
| **Cashier / Shop Employee** | The Cashier performs sales and returns. They may view inventory levels but cannot modify them. Their interest is in a system that is fast, easy to learn, and minimizes errors. |
| **Customer** | The end-user of the shop. Customers interact indirectly with the system through the checkout process or directly via the mobile/online application.. Their interests are a fast and error-free checkout, accurate pricing, and a clear receipt. |
| **Supplier** | The external B2B entity that provides the shop with its products Their interest is receiving clear, accurate, and timely Purchase Orders from the system. |
| **Accountant** | The Accountant has read-only access to financial data and is responsible for tax tracking and preparing financial statements. Their interest is the ability to easily access and export accurate, detailed financial reports. |
| **Maintenance staff** | The Maintenance Staff provides technical support and system updates. They do not manage business data but ensure the system operates correctly. |
| **External Payment System** | The third-party service and hardware (e.g., credit card terminal/provider) that processes electronic payments via a secure interface. This is an external system actor. Its "interest" is receiving correct payment totals from EZShop and returning a clear "approved" or "denied" status via a secure interface. |
| **Warehouse worker** | People responsible to count the items’ stock and to manage the incoming supplier products |
| **Products** | Items in the shop inventory which have many attributes: name, description, bar code, boolean value which indicates if it is available or not, possible discounts, price. |

# Context Diagram and interfaces

## Context Diagram

\<Define here Context diagram using UML use case diagram>

\<actors are a subset of stakeholders>

## Interfaces

| Actor | Logical Interface | Physical Interface |
| :----: | :---- | :---- |
| **Cashier** | **Point of Sale (POS) UI:** A graphical user interface designed for fast transaction processing.  | **Cash Register Terminal:** A dedicated computer, barcode scanner, thermal receipt printer and a physical Cash Drawer. |
| **Shop Owner** | **Management Dashboard:** A secure, web-based administrative interface. It provides access to all management functions: product catalog, inventory levels, supplier orders, sales reports, and user account management. | **PC, Laptop, or Tablet:** Any device with a modern web browser and an internet connection. |
| **Accountant** | **Reporting Interface:** A secure, web-based interface focused on financial data. It allows for viewing and exporting reports on sales, taxes, and purchases. | **PC or Laptop:** A standard computer with a web browser.  |
| **Supplier System** | **Order Interface:** An automated or manual interface for sending a Purchase Order. | **Any device with email system:** The system generates and sends a formatted email, often with a **PDF** attachment of the Purchase Order, to the supplier's contact email address. |
| **Customer** | **Mobile app:** An application where the customer can independently order the items of the shop | **Pc, laptop, tablet, smartphone:** any device with the application installed |
| **Warehouse worker** | **Notification interface:** an interface with which the worker can notify anything to the system | **Main computer:** the main computer from where the system will receive important notification from the Warehouse workers |
| **Payment System** | **Credit card circuit api:** terminal interface, online bank system | Credit card reader, cash drawer, mobile app/ web browser |

# Functional and non functional requirements

## Functional Requirements

| ID | Description | Subrequirements |
| :---- | :---- | :---- |
| **FR1** | **Manage In-Store Sales** | **FR1.1: Add Items**<br><ul><li>**FR1.1.1:** Add product via barcode scanning</li> <li>**FR1.1.2:** Add product via manual search</li> <li>**FR1.1.3:** Update and display subtotal</li> <li>**FR1.1.4:** Require ID for restricted items</li></ul> **FR1.2: Remove Items** <br><ul><li>**FR1.2.1:** Remove product from the order</li> <li>**FR1.2.2:** Update subtotal after removal</li></ul> **FR1.3: Select Card Payment** <br><ul><li>**FR1.3.1:** Send total amount to payment system</li> <li>**FR1.3.2:** Wait for approval or denial</li><li> **FR1.3.3:** Complete sale on approval</li><li> **FR1.3.4:** Display error on denial</li></ul> **FR1.4: Select Cash Payment** <br><ul><li>**FR1.4.1:** Display total amount</li><li> **FR1.4.2:** Open cash drawer</li><li> **FR1.4.3:** Calculate change</li></ul> **FR1.5: Complete Sale**<br><ul><li> **FR1.5.1:** Generate sales receipt</li><li> **FR1.5.2:** Store transaction</li><li> **FR1.5.3:** Update inventory</li></ul> **FR1.6: Error Handling** <br><ul><li> **FR1.6.1:** Unknown barcode error</li><li> **FR1.6.2:** Block incomplete payments</li><li> **FR1.6.3:** Notify POS hardware issues</li></ul> |
| **FR2** | **Manage Online Customer Orders** | **FR2.1: Add Items to Cart FR2.1.1:** Add product to shopping cart **FR2.1.2:** Display item name, price and updated subtotal **FR2.2: Remove Items from Cart FR2.2.1:** Remove items from shopping cart **FR2.2.2:** Update the subtotal accordingly **FR2.3: Checkout FR2.3.1:** DIsplay the subtotal, taxes and final total **FR2.4: Select Payment Method FR2.4.1:** Select online payment method **FR2.4.2:** Send the total amount to the Online Payment System **FR2.4.3:** Complete the order only if payment is approved **FR2.4.4:** Display an error message if payment or denied **FR2.5: Receipt FR2.5.1:** Generate a digital receipt **FR2.5.2:** Send the receipt via email to the customer **FR2.6: Request Refound FR2.6.1:** Enable customer to request a refund for purchased items **FR2.6.2:** Require a receipt or transaction ID for refounds **FR2.6.3:** Forward the refund request to the Cashier/Owner for approval **FR2.7: Error Handling FR2.7.1:** Restore cart if  payment fails **FR2.7.2:** Payment system downtime message |
| **FR3** | **Manage Returns** | **FR3.1: Verify Return Eligibility FR3.1.1:** Validate existence of original purchase **FR3.1.2:** Display the item details and the refundable amount **FR3.1.3:** Notify the staff if the item is non-returnable or the sale cannot be found **FR3.2: Select Return Method FR3.2.1:** Provide option to choose a return method (in-store or courier) **FR3.2.2:** For in-store returns, the system shall require presenting the physical receipt **FR3.2.3:** For courier returns, the system shall require uploading a PDF receipt or providing the transaction ID **FR3.3: Approve or Reject Return FR3.3.1:** Enable authorized staff (Cashier/Owner) to approve or reject a return request **FR3.3.2:** Record the decision and apply it to the transaction history **FR3.4: Process Refund FR3.4.1:** Support multiple refund types (cash, card, store credit) **FR3.4.2:** Send refund request to the External Payment System (for card refunds) **FR3.4.3:** Complete the refund only after receiving approval from the External Payment System **FR3.4.4:** Notify the staff if the refund is denied (Error on denial) **FR3.5: Generate Return Receipt FR3.5.1:** Generate a return receipt for the customer **FR3.5.2:** Store return receipts in the system database **FR3.6: Error Handling FR3.6.1:** Display an error when the provided receipt or transaction ID is invalid **FR3.6.2:** Block incomplete refund **FR3.6.3:** Notify the staff if required POS or payment hardware is not available |
| **FR4** | **Manage Products** | **FR4.1: Add Product FR4.1.1:** Enter product name, description, supplier, barcode, price, initial stock level **FR4.1.2:** Validate unique barcode **FR4.1.3:** Create product entry **FR4.2: Delete Product FR 4.2.1:** Delete selected product **FR 4.2.2:** Prevent deletion if product is linked to completed transactions **FR4.3: Modify Product FR4.3.1:** Edit product name **FR4.3.2:** Edit description **FR4.3.3:** Edit supplier **FR4.3.4:** Edit price **FR4.3.5:** Add discounts **FR4.3.6:** Add threshold **FR4.3.7:** Validate fields before save **FR4.4: Availability FR4.4.1:** Automatically mark product as unavailable if stock \= 0 **FR4.4.2:** Manually set unavailable **FR4.5: View Product FR4.5.1:** View full product details **FR4.5.2:** View stock levels and supplier info **FR4.6: Error Handling FR4.6.1:** Missing field error **FR4.6.2:** Invalid price error **FR4.6.3:** Duplicate barcode error  |
| **FR5** | **Manage Inventory** | **FR5.1:** **Automatic Stock Updates FR5.1.1:** Decrease stock after completing an in-store sale (FR1) **FR5.1.2:** Decrease stock after completing an online sale (FR2) **FR5.1.3:** Increase stock after a completed return (FR3) **FR5.1.4:** Increase stock when items from supplier are confirmed (FR6) **FR5.2: Manual Stock Adjustments FR5.2.1:** Manually adjust stock levels for any product **FR5.2.2:** Log every manual adjustment for auditing purposes |
| **FR6** | **Manage Supplier Orders** | **FR6.1: Create Supplier Orders FR6.1.1:** Create a new purchase order for selected products **FR6.1.2:** Include product quantities, supplier information, and total cost **FR6.1.3:** Save purchase orders as drafts before sending **FR6.2:** **Send Purchase Orders** **FR6.2.1:** Generate a formatted purchase order document (e.g., PDF) **FR6.2.2:** Send purchase orders to suppliers via email **FR6.2.3:** Mark purchase orders as “sent” after successful delivery **FR6.3: Automatic Restocking FR6.3.1:** Trigger automatic purchase orders when stock falls below threshold **FR6.4: Manage Order Status FR6.4.1:** Track purchase order states (draft, sent, delivered, completed) **FR6.4.2:** Log changes in order status for auditing and traceability **FR6.5: Error Handling FR6.5.1:** Display error for missing or invalid supplier information **FR6.5.2:** Display error if email delivery fails **FR6.5.3:** Warn if received stock quantity does not match the purchase order |
| **FR7** | **Generate Reports** | **FR7.1: Daily Sales Summary FR7.1.1:** Produce a daily summary of all completed orders **FR7.1.2:** Display total income for the day **FR7.1.3:** Display total losses (e.g., returned items, discarded stock) **FR7.1.4:** Display total taxes **FR7.2: Restock Notifications FR7.2.1:** Notify the Owner when an automatic restock order is generated **FR7.3: Financial Reports FR7.3.1:** Provide access to financial statistics (sales, taxes, refunds) **FR7.3.2:** Allow exporting financial reports for accounting purposes **FR7.4: Error Handling FR7.4.1:** Display error if report data is incomplete or unavailable **FR7.4.2:** Warn if report generation exceeds time limits **FR7.4.3:** Notify the user if exporting fails |
| **FR8** | **Manage Users** | **FR8.1: Owner Account Creation FR8.1.1:** Create an Owner account during initial system setup **FR8.1.2:** Allow the Owner to define the address of physical shop associated with the account **FR8.2: Cashier Accounts FR8.2.1:** Create Cashier accounts **FR8.2.2:** Add employment contract **FR8.2.3:** Require Cashiers to log in before accessing the POS **FR8.2.4:** Restrict Cashier access to POS functions only **FR8.3: Accountant Accounts FR8.3.1:** Create Accountant accounts **FR8.3.2:** Add agreement contract **FR8.3.3:** Limit Accountant access to financial reports and related data **FR8.4: Customer Accounts FR8.4.1:** Allow account creation for online customers **FR8.4.2:** Add credit card **FR8.4.3:** Add IBAN **FR8.4.4:** Limit customer account to placing orders and requesting refounds functions only **FR8.4.5:** Store customer purchase history and digital receipts **FR8.5: Warehouse Worker Account FR8.5.1:** Create Warehouse worker accounts **FR8.5.2:** Add warehouse section **FR8.5.3:** Limit warehouse workers account to stocks function only **FR8.6: Account Deactivation and Deletion (Owner) FR8.6.1:** Deactivate or delete Cashier accounts **FR8.6.2:** Deactivate or delete Customer accounts **FR8.6.3:** Deactivate or delete Accountant accounts **FR8.6.4:** Deactivate or delete Warehouse worker accounts **FR8.7: Error Handling FR8.7.1:** Display error when mandatory user information is missing **FR8.7.2:** Display error for duplicate usernames or email addresses **FR8.7.3:** Warn when user role assignment is invalid |
| **FR9** | **Manage Physical Stocks** | **FR9.1: Stock Corrections FR9.1.1:** Enable correcting digital stock levels **FR9.1.2:** Log all corrections for auditing and traceability **FR9.1.3:** Prevent corrections that result in negative stock quantities **FR9.2: Incoming Goods Verification FR9.2.1:** Record quantities received from supplier deliveries **FR9.2.2:** Compare delivered quantities with purchase orders **FR9.2.3:** Notify the Owner of delivery inconsistencies |
| **FR10** | **Managing financial issues** | **FR10.1: Track Financial Information FR10.1.1:** Record all sales transactions for financial reporting **FR10.1.2:** Record all refunds and returns (FR3) **FR10.1.3:** Record all restock orders and supplier payments (FR6) **FR10.2: Taxes and Accounting FR10.2.1:** Calculate applicable taxes on each sale **FR10.2.2:** Include tax information in financial summaries **FR10.2.3:** Provide tax data required for external accounting **FR10.3: Financial Reporting FR10.3.1:** Generate financial summary reports (income, expenses, refunds) **FR10.3.2:** Provide detailed breakdowns of sales, losses, and taxes **FR10.3.3:** Allow exporting financial reports for external accounting tools **FR10.4: Payment Reconciliation FR10.4.1:** Match digital transaction records with payment-system confirmations **FR10.4.2:** Identify inconsistencies between POS payments and system records **FR10.4.3:** Notify Owner and Accountant when mismatches occur **FR10.5: Financial Audit Support FR10.5.1:** Log all financial operations for audit purposes **FR10.5.2:** Provide access to historical financial data **FR10.5.3:** Prevent unauthorized modification of financial records **FR10.6: Error Handling FR10.6.1:** Display error for missing or inconsistent financial data **FR10.6.2:** Warn when report generation fails or data is incomplete **FR10.6.3:** Prevent financial computations using invalid values |

## Non Functional Requirements

\<Describe constraints on functional requirements>

|   ID    | Type (efficiency, reliability, ..) | Description | Refers to |
| :-----: | :--------------------------------: | :---------: | :-------: |
|  NFR1   |                                    |             |           |
|  NFR2   |                                    |             |           |
|  NFR3   |                                    |             |           |
| NFRx .. |                                    |             |           |

# Table of rights

|  Actor   | FR1         | FRx |
| :---:    | :---------: | :---: |
|          |             |       |

# Use case diagram and use cases

## Use case brief
|  UC name   | Goal         | Description |
| :---:    | :---------: | :---: |
|          |             |       |



## Use case diagram

\<define here UML Use case diagram UCD summarizing all use cases, and their relationships>

\<next describe here each use case in the UCD>

### Use case 1, UC1

| Actors Involved  |                                                                      |
| :--------------: | :------------------------------------------------------------------: |
|   Precondition   | \<Boolean expression, must evaluate to true before the UC can start> |
|  Post condition  |  \<Boolean expression, must evaluate to true after UC is finished>   |
| Nominal Scenario |         \<Textual description of actions executed by the UC>         |
|     Variants     |                      \<other normal executions>                      |
|    Exceptions    |                        \<exceptions, errors >                        |

##### Scenario 1.1

\<describe here scenarios instances of UC1>

\<a scenario is a sequence of steps that corresponds to a particular execution of one use case>

\<a scenario is a more formal description of a story>

\<only relevant scenarios should be described>

|  Scenario 1.1  |                                                                            |
| :------------: | :------------------------------------------------------------------------: |
|  Precondition  | \<Boolean expression, must evaluate to true before the scenario can start> |
| Post condition |  \<Boolean expression, must evaluate to true after scenario is finished>   |


Steps

|     Actor's action      |  System action                                                                    | FR needed |
| :------------: | :------------------------------------------------------------------------: |:---:|
|               |                                                                 |  |
|   |  |  |
##### Scenario 1.2

##### Scenario 1.x

### Use case 2, UC2

..

### Use case x, UCx

..

# Glossary

\<use UML class diagram to define important terms, or concepts in the domain of the application, and their relationships>

\<concepts must be used consistently all over the document, ex in use cases, requirements etc>

# System Design

\<describe here system design>

\<must be consistent with Context diagram>

# Hardware Software architecture

\<describe here the hardware software architecture using UML deployment diagram >
