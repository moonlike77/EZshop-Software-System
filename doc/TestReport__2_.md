# Test Report

\<The goal of this document is to explain how the application was tested, detailing how the test cases were defined and what they cover\>

# Contents

* [Test Report](#test-report)  
* [Contents](#contents)  
* [Dependency graph](#dependency-graph)  
* [Integration approach](#integration-approach)  
* [Tests](#tests)  
* [Coverage](#coverage)  
  * [Coverage of FR](#coverage-of-fr)  
  * [Coverage white box](#coverage-white-box)

# Dependency graph

    <report the here the dependency graph of EzShop>


# Integration approach

    The integration sequence adopted was a bottom up:

    step1: all the repositories

    step2: all the controllers + repositories

    step3: all the routes + controllers + repositories

# Tests

 **Product API Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| :---: | :---: | :---: | :---: |
| test\_create\_product\_e2e | POST /api/v1/products | API | BB / Equivalence Partitioning |
| test\_create\_product\_minimal\_e2e | POST /api/v1/products | API | BB / Equivalence Partitioning |
| test\_get\_product\_by\_id\_e2e | GET /api/v1/products/{id} | API | BB / Equivalence Partitioning |
| test\_get\_product\_by\_barcode\_e2e | GET /api/v1/products/barcode/{barcode} | API | BB / Equivalence Partitioning |
| test\_get\_all\_products\_e2e | GET /api/v1/products | API | BB / Equivalence Partitioning |
| test\_search\_products\_e2e | GET /api/v1/products?description={query} | API | BB / Equivalence Partitioning |
| test\_update\_product\_e2e | PUT /api/v1/products/{id} | API | WB / Statement Coverage |
| test\_update\_quantity\_e2e | PATCH /api/v1/products/{id}/quantity | API | WB / Statement Coverage |
| test\_update\_position\_e2e | PATCH /api/v1/products/{id}/position | API | WB / Statement Coverage |
| test\_delete\_product\_e2e | DELETE /api/v1/products/{id} | API | WB / Statement Coverage |
| test\_create\_product\_unauthorized\_e2e | POST /api/v1/products | API | BB / Error Guessing |
| test\_create\_duplicate\_barcode\_e2e | POST /api/v1/products | API | BB / Boundary Value |
| test\_invalid\_position\_format\_e2e | POST /api/v1/products | API | BB / Boundary Value |

 **Product Integration Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| :---: | :---: | :---: | :---: |
| test\_product\_bottom\_up\_crud\_flow | ProductController | Integration | BB / Output Validation |
| test\_product\_bottom\_up\_not\_found\_paths | ProductController | Integration | BB / Error Guessing |
| test\_product\_bottom\_up\_duplicate\_barcode\_conflict | ProductController | Integration | BB / Boundary Value |
| test\_product\_bottom\_up\_update\_barcode\_conflict | ProductController | Integration | BB / Boundary Value |
| test\_product\_bottom\_up\_position\_format\_validation | ProductController | Integration | BB / Input Validation |
| test\_product\_bottom\_up\_position\_uniqueness\_conflict | ProductController | Integration | BB / Boundary Value |
| test\_product\_bottom\_up\_update\_quantity\_cannot\_go\_negative | ProductController | Integration | BB / Boundary Value |
| test\_product\_put\_update\_rejects\_position\_field | ProductController | Integration | BB / Input Validation |
| test\_product\_bottom\_up\_crud\_flow | ProductController | Integration | BB / Output Validation |
| test\_product\_bottom\_up\_not\_found\_paths | ProductController | Integration | BB / Error Guessing |
| test\_product\_bottom\_up\_duplicate\_barcode\_conflict | ProductController | Integration | BB / Boundary Value |
| test\_product\_bottom\_up\_update\_barcode\_conflict | ProductController | Integration | BB / Boundary Value |
| test\_product\_bottom\_up\_position\_format\_validation | ProductController | Integration | BB / Input Validation |

   
**Product Unit Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| :---: | :---: | :---: | :---: |
| test\_create\_product\_success | ProductRepository | Unit | WB / Statement Coverage |
| test\_create\_product\_minimal | ProductRepository | Unit | WB / Statement Coverage |
| test\_create\_product\_duplicate\_barcode | ProductRepository | Unit | BB / Error Guessing |
| test\_get\_product\_by\_id\_success | ProductRepository | Unit | WB / Statement Coverage |
| test\_get\_product\_by\_id\_not\_found | ProductRepository | Unit | BB / Error Guessing |
| test\_get\_product\_by\_barcode\_success | ProductRepository | Unit | WB / Statement Coverage |
| test\_get\_product\_by\_barcode\_not\_found | ProductRepository | Unit | BB / Error Guessing |
| test\_get\_all\_products\_empty | ProductRepository | Unit | BB / Boundary Value |
| test\_get\_all\_products\_success | ProductRepository | Unit | WB / Statement Coverage |
| test\_search\_products\_by\_description\_found | ProductRepository | Unit | BB / Equivalence Partitioning |
| test\_search\_products\_by\_description\_not\_found | ProductRepository | Unit | BB / Boundary Value |
| test\_search\_products\_case\_insensitive | ProductRepository | Unit | BB / Equivalence Partitioning |
| test\_update\_product\_all\_fields | ProductRepository | Unit | WB / Statement Coverage |

**Order API Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| :---: | :---: | :---: | :---: |
| test\_create\_and\_pay\_order\_e2e | POST /api/v1/orders/payfor | API | BB / Equivalence Partitioning |
| test\_create\_and\_pay\_order\_insufficient\_balance\_e2e | POST /api/v1/orders/payfor | API | BB / Boundary Value |
| test\_delete\_order\_not\_found\_e2e | DELETE /api/v1/orders/{id} | API | BB / Error Guessing |
| test\_pay\_reorder\_warning\_not\_found\_e2e | PATCH /api/v1/orders/{id}/pay-reorder | API | BB / Error Guessing |
| test\_issue\_reorder\_warning\_missing\_product\_e2e | POST /api/v1/orders/reorder | API | BB / Error Guessing |
| test\_create\_and\_pay\_order\_e2e | POST /api/v1/orders/payfor | API | BB / Equivalence Partitioning |
| test\_create\_and\_pay\_order\_insufficient\_balance\_e2e | POST /api/v1/orders/payfor | API | BB / Boundary Value |
| test\_delete\_order\_not\_found\_e2e | DELETE /api/v1/orders/{id} | API | BB / Error Guessing |
| test\_pay\_reorder\_warning\_not\_found\_e2e | PATCH /api/v1/orders/{id}/pay-reorder | API | BB / Error Guessing |
| test\_issue\_reorder\_warning\_missing\_product\_e2e | POST /api/v1/orders/reorder | API | BB / Error Guessing |
| test\_create\_and\_pay\_order\_e2e | POST /api/v1/orders/payfor | API | BB / Equivalence Partitioning |
| test\_create\_and\_pay\_order\_insufficient\_balance\_e2e | POST /api/v1/orders/payfor | API | BB / Boundary Value |
| test\_delete\_order\_not\_found\_e2e | DELETE /api/v1/orders/{id} | API | BB / Error Guessing |

**Order Integration Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| :---: | :---: | :---: | :---: |
| test\_order\_bottom\_up\_create\_pay\_arrive\_flow | OrderController | Integration | BB / Output Validation |
| test\_order\_bottom\_up\_delete\_then\_not\_found | OrderController | Integration | BB / State Transition |
| test\_order\_bottom\_up\_not\_found\_paths | OrderController | Integration | BB / Error Guessing |
| test\_order\_bottom\_up\_create\_order\_missing\_product | OrderController | Integration | BB / Error Guessing |
| test\_order\_bottom\_up\_pay\_requires\_sufficient\_balance | OrderController | Integration | BB / Boundary Value |
| test\_order\_bottom\_up\_pay\_invalid\_state\_cannot\_pay\_twice | OrderController | Integration | BB / State Transition |
| test\_order\_bottom\_up\_arrival\_invalid\_state\_requires\_paid | OrderController | Integration | BB / State Transition |
| test\_order\_bottom\_up\_arrival\_requires\_product\_position | OrderController | Integration | BB / Boundary Value |
| test\_order\_bottom\_up\_create\_pay\_arrive\_flow | OrderController | Integration | BB / Output Validation |
| test\_order\_bottom\_up\_delete\_then\_not\_found | OrderController | Integration | BB / State Transition |
| test\_order\_bottom\_up\_not\_found\_paths | OrderController | Integration | BB / Error Guessing |
| test\_order\_bottom\_up\_create\_order\_missing\_product | OrderController | Integration | BB / Error Guessing |
| test\_order\_bottom\_up\_pay\_requires\_sufficient\_balance | OrderController | Integration | BB / Boundary Value |

**Order Unit Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| :---: | :---: | :---: | :---: |
| test\_create\_order\_success | OrderRepository | Unit | WB / Statement Coverage |
| test\_get\_order\_success | OrderRepository | Unit | WB / Statement Coverage |
| test\_get\_order\_not\_found | OrderRepository | Unit | BB / Error Guessing |
| test\_get\_all\_orders\_empty | OrderRepository | Unit | BB / Boundary Value |
| test\_get\_all\_orders\_success | OrderRepository | Unit | WB / Statement Coverage |
| test\_pay\_order\_success | OrderRepository | Unit | WB / Statement Coverage |
| test\_pay\_order\_not\_found | OrderRepository | Unit | BB / Error Guessing |
| test\_pay\_order\_wrong\_status | OrderRepository | Unit | BB / State Transition |
| test\_pay\_order\_insufficient\_balance | OrderRepository | Unit | BB / Boundary Value |
| test\_record\_order\_arrival\_success | OrderRepository | Unit | WB / Statement Coverage |
| test\_record\_arrival\_not\_found | OrderRepository | Unit | BB / Error Guessing |
| test\_record\_arrival\_wrong\_status | OrderRepository | Unit | BB / State Transition |
| test\_create\_order\_success | OrderRepository | Unit | WB / Statement Coverage |

**Customer API Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| :---: | :---: | :---: | :---: |
| test\_create\_customer\_success | POST /customers | API  | BB/ eq partitioning |
| test\_create\_customer\_bad\_request | POST /customers | API  | BB/ eq partitioning |
| test\_get\_all\_customers\_success | GET /customers | API  | BB/ eq partitioning |
| test\_get\_customer\_success | GET /customers/{customer\_id} | API | BB/ eq partitioning |
| test\_get\_customer\_invalid\_id | GET /customers/{customer\_id} | API | BB/ eq partitioning |
| test\_get\_customer\_not\_found | GET /customers/{customer\_id} | API | BB/ eq partitioning |
| test\_update\_customer\_success | PUT /customers/{customer\_id} | API | BB/ eq partitioning |
| test\_update\_customer\_invalid\_id | PUT /customers/{customer\_id} | API | BB/ eq partitioning |
| test\_update\_customer\_invalid\_payload | PUT /customers/{customer\_id} | API | BB/ eq partitioning |
| test\_update\_customer\_not\_found | PUT /customers/{customer\_id} | API | BB/ eq partitioning |
| test\_create\_loyalty\_card\_success | POST /customers/cards | API | BB/ eq partitioning |
| test\_attach\_loyalty\_card\_to\_customer\_success | PATCH /customers/{customer\_id}/attach-card/{card\_id} | API | BB/ eq partitioning |
| test\_attach\_card\_not\_found\_error | PATCH /customers/{customer\_id}/attach-card/{card\_id} | API | BB/ eq partitioning |
| test\_attach\_card\_conflict\_error | PATCH /customers/{customer\_id}/attach-card/{card\_id} | API | BB/ eq partitioning |
| test\_update\_loyalty\_card\_points\_success | PATCH /customers/cards/{card\_id}?points={points} | API | BB/ eq partitioning |
| test\_delete\_customer\_success | DELETE /customers/{customer\_id} | API | BB/ eq partitioning |
| test\_delete\_customer\_not\_found | DELETE /customers/{customer\_id} | API | BB/ eq partitioning |

**Customer Integration Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| :---: | :---: | :---: | :---: |
| test\_create\_customer\_without\_card | CustomerController.create\_customer() | Integration | BB/ eq partitioning |
| test\_create\_loyalty\_card | LoyaltyCardController.create\_loyalty\_card() | Integration | BB/ eq partitioning |
| test\_create\_customer\_with\_card | CustomerController.create\_customer() | Integration | BB/ eq partitioning |
| test\_get\_customer | CustomerController.get\_customer() | Integration | BB/ eq partitioning |
| test\_get\_customer\_not\_found | CustomerController.get\_customer() | Integration | BB/ eq partitioning |
| test\_get\_loyalty\_card | LoyaltyCardController.get\_loyalty\_card() | Integration | BB/ eq partitioning |
| test\_get\_loyalty\_card\_not\_found | LoyaltyCardController.get\_loyalty\_card() | Integration | BB/ eq partitioning |
| test\_list\_customers | CustomerController.list\_customers() | Integration | BB/ eq partitioning |
| test\_list\_customers\_empty | CustomerController.list\_customers() | Integration | BB/ eq partitioning |
| test\_update\_loyalty\_card\_points | LoyaltyCardController.update\_loyalty\_card\_points() | Integration | BB/ eq partitioning |
| test\_update\_loyalty\_card\_points\_not\_found | LoyaltyCardController.update\_loyalty\_card\_points() | Integration | BB/ eq partitioning |
| test\_update\_customer\_name\_and\_card\_fixed | CustomerController.update\_customer() | Integration | BB/ eq partitioning |
| test\_update\_customer\_name\_and\_card\_customer\_not\_found | CustomerController.update\_customer() | Integration | BB/ eq partitioning |
| test\_update\_customer\_delte\_card | CustomerController.update\_customer() | Integration | BB/ eq partitioning |
| test\_attach\_loyalty\_card\_to\_customer | CustomerController.attach\_loyalty\_card\_to\_customer() | Integration | BB/ eq partitioning |
| test\_attach\_loyalty\_card\_to\_customer\_customer\_not\_found | CustomerController.attach\_loyalty\_card\_to\_customer() | Integration | BB/ eq partitioning |
| test\_delete\_customer | CustomerController.delete\_customer() | Integration | BB/ eq partitioning |
| test\_delete\_customer\_not\_found | CustomerController.delete\_customer() | Integration | BB/ eq partitioning |
| test\_delete\_loyalty\_card | LoyaltyCardController.delete\_loyalty\_card() | Integration | BB/ eq partitioning |
| test\_delete\_loyalty\_card\_not\_found | LoyaltyCardController.delete\_loyalty\_card() | Integration | BB/ eq partitioning |

**Customer Unit Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| :---: | :---: | :---: | :---: |
| test\_create\_customer\_success | CustomerRepository.create\_customer() | Unit | BB/ eq partitioning |
| test\_create\_loyalty\_card\_success | LoyaltyCardRepository.create\_loyalty\_card() | Unit  | BB/ eq partitioning |
| test\_create\_customer\_conflict | CustomerRepository.create\_customer() | Unit  | BB/ eq partitioning |
| test\_get\_customer\_success | CustomerRepository.get\_customer() | Unit  | BB/ eq partitioning |
| test\_get\_loyalty\_card\_success | LoyaltyCardRepository.get\_loyalty\_card() | Unit  | BB/ eq partitioning |
| test\_get\_customer\_not\_found | CustomerRepository.get\_customer() | Unit  | BB/ eq partitioning |
| test\_get\_loyalty\_card\_not\_found | LoyaltyCardRepository.get\_loyalty\_card() | Unit  | BB/ eq partitioning |
| test\_list\_customers\_empty | CustomerRepository.list\_customers() | Unit  | BB/ eq partitioning |
| test\_list\_customers\_success | CustomerRepository.list\_customers() | Unit  | BB/ eq partitioning |
| test\_update\_loyalty\_card\_points\_success | LoyaltyCardRepository.update\_loyalty\_card\_points() | Unit  | BB/ eq partitioning |
| test\_update\_loyalty\_card\_points\_not\_enough\_points | LoyaltyCardRepository.update\_loyalty\_card\_points() | Unit  | BB/ eq partitioning |
| test\_update\_loyalty\_card\_points\_not\_found | LoyaltyCardRepository.update\_loyalty\_card\_points() | Unit  | BB/ eq partitioning |
| test\_update\_customer\_card\_success | CustomerRepository.update\_customer\_card() | Unit  | BB/ eq partitioning |
| test\_update\_customer\_card\_customer\_not\_found | CustomerRepository.update\_customer\_card() | Unit  | BB/ eq partitioning |
| test\_update\_customer\_card\_loyalty\_card\_not\_found | CustomerRepository.update\_customer\_card() | Unit  | BB/ eq partitioning |
| test\_update\_customer\_card\_already\_attached\_to\_him | CustomerRepository.update\_customer\_card() | Unit  | BB/ eq partitioning |
| test\_update\_customer\_card\_already\_attached\_to\_other | CustomerRepository.update\_customer\_card() | Unit  | BB/ eq partitioning |
| test\_update\_customer\_only\_name\_success | CustomerRepository.update\_customer() | Unit  | BB/ eq partitioning |
| test\_update\_customer\_only\_name\_not\_found | CustomerRepository.update\_customer() | Unit  | BB/ eq partitioning |
| test\_update\_customer\_only\_name\_conflict\_on\_name | CustomerRepository.update\_customer() | Unit  | BB/ eq partitioning |
| test\_update\_customer\_only\_card\_success | CustomerRepository.update\_customer() | Unit  | BB/ eq partitioning |
| test\_update\_customer\_detach\_card\_success | CustomerRepository.update\_customer() | Unit  | BB/ eq partitioning |
| test\_delete\_customer\_success | CustomerRepository.delete\_customer() | Unit  | BB/ eq partitioning |
| test\_delete\_loyalty\_card\_success | LoyaltyCardRepository.delete\_loyalty\_card() | Unit  | BB/ eq partitioning |
| test\_delete\_customer\_not\_found | CustomerRepository.delete\_customer() | Unit  | BB/ eq partitioning |
| test\_delete\_loyalty\_card\_not\_found | LoyaltyCardRepository.delete\_loyalty\_card() | Unit | BB/ eq partitioning |

**Return API Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| :---- | :---- | :---- | :---- |
| test\_start\_return\_route | POST /api/v1/returns/ | API | BB / Equivalence Partitioning |
| test\_start\_return\_route\_sale\_not\_found | POST /api/v1/returns/ | API | BB / Error Guessing |
| test\_get\_all\_returns\_route | GET /api/v1/returns/ | API | BB / Equivalence Partitioning |
| test\_get\_all\_returns\_by\_sale\_route | GET /api/v1/returns/sale/{id} | API | BB / Equivalence Partitioning |
| test\_get\_return\_route | GET /api/v1/returns/{id} | API | BB / Equivalence Partitioning |
| test\_get\_return\_route\_not\_found | GET /api/v1/returns/{id} | API | BB / Error Guessing |
| test\_add\_product\_to\_return\_route | POST /api/v1/returns/{id}/items | API | BB / Equivalence Partitioning |
| test\_add\_product\_to\_return\_route\_not\_found | POST /api/v1/returns/{id}/items | API | BB / Error Guessing |
| test\_delete\_product\_from\_return\_route | DELETE /api/v1/returns/{id}/items | API | BB / Equivalence Partitioning |
| test\_delete\_product\_from\_return\_route\_not\_found | DELETE /api/v1/returns/{id}/items | API | BB / Error Guessing |
| test\_close\_return\_route | PATCH /api/v1/returns/{id}/close | API | BB / State Transition |
| test\_close\_return\_route\_not\_found | PATCH /api/v1/returns/{id}/close | API | BB / Error Guessing |
| test\_reimburse\_return\_route | PATCH /api/v1/returns/{id}/reimburse | API | BB / State Transition |
| test\_reimburse\_return\_route\_not\_found | PATCH /api/v1/returns/{id}/reimburse | API | BB / Error Guessing |
| test\_delete\_return\_route | DELETE /api/v1/returns/{id} | API | BB / Equivalence Partitioning |
| test\_delete\_return\_route\_not\_found | DELETE /api/v1/returns/{id} | API | BB / Error Guessing |

**Return Integration Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| :---- | :---- | :---- | :---- |
| test\_start\_return | ReturnController.start\_return | Integration | BB / Output Validation |
| test\_get\_return\_success | ReturnController.get\_return | Integration | BB / Equivalence Partitioning |
| test\_get\_return\_not\_found | ReturnController.get\_return | Integration | BB / Error Guessing |
| test\_list\_all\_returns\_success | ReturnController.list\_returns | Integration | BB / Equivalence Partitioning |
| test\_get\_all\_returns\_by\_sale\_success | ReturnController.get\_returns\_by\_sale | Integration | BB / Equivalence Partitioning |
| test\_add\_product\_to\_return\_success | ReturnController.add\_item | Integration | BB / Output Validation |
| test\_remove\_product\_from\_return\_success | ReturnController.remove\_item | Integration | BB / Output Validation |
| test\_add\_product\_to\_return\_not\_found | ReturnController.add\_item | Integration | BB / Error Guessing |
| test\_remove\_product\_from\_return\_not\_found | ReturnController.remove\_item | Integration | BB / Error Guessing |
| test\_add\_product\_to\_return\_invalid\_state | ReturnController.add\_item | Integration | BB / State Transition |
| test\_remove\_product\_from\_return\_invalid\_state | ReturnController.remove\_item | Integration | BB / State Transition |
| test\_close\_return\_success | ReturnController.close\_return | Integration | BB / State Transition |
| test\_close\_return\_fail\_if\_not\_open | ReturnController.close\_return | Integration | BB / State Transition |
| test\_close\_return\_not\_found | ReturnController.close\_return | Integration | BB / Error Guessing |
| test\_close\_empty\_return\_with\_deletion | ReturnController.close\_return | Integration | BB / Boundary Value Analysis |
| test\_reimburse\_return\_success | ReturnController.reimburse\_return | Integration | BB / State Transition |
| test\_reimburse\_return\_not\_found | ReturnController.reimburse\_return | Integration | BB / Error Guessing |
| test\_reimburse\_return\_invalid\_state | ReturnController.reimburse\_return | Integration | BB / State Transition |
| test\_delete\_return\_success | ReturnController.delete\_return | Integration | BB / Output Validation |
| test\_delete\_return\_not\_found | ReturnController.delete\_return | Integration | BB / Error Guessing |
| test\_delete\_return\_fail\_if\_reimbursed | ReturnController.delete\_return | Integration | BB / State Transition |

### 

**Return Unit Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| :---- | :---- | :---- | :---- |
| test\_create\_and\_get\_returns\_also\_with\_invalid\_sale\_state | ReturnRepository.create\_return | Unit | WB / Statement Coverage |
| test\_add\_and\_remove\_line\_all\_cases | ReturnRepository.add\_line | Unit | WB / Path Coverage |
| test\_update\_status | ReturnRepository.update\_status | Unit | WB / Statement Coverage |

**Sale API Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| ----- | :---: | :---: | :---: |
| test\_start\_sale\_success | POST/sales | API  | BB / eq partitioning  |
| test\_start\_sale\_unauthorized | POST/sales | API  | BB / eq partitioning |
| test\_get\_all\_sales\_success | GET/sales | API  | BB / eq partitioning |
| test\_get\_all\_sales\_empty | GET/sales | API | BB / eq partitioning |
| test\_get\_all\_sales\_unauthorized | GET/sales | API | BB / eq partitioning |
| test\_get\_sale\_success | GET/sales/{sale\_id} | API | BB / eq partitioning |
| test\_get\_sale\_invalid\_id | GET/sales/{sale\_id} | API | BB / boundary |
| test\_delete\_sale\_success | DELETE/sales/{sale\_id} | API | BB / eq partitioning |
| test\_delete\_sale\_invalid\_id | DELETE/sales/{sale\_id} | API | BB / boundary |
| test\_add\_product\_success | POST/sales/{sale\_id}/items | API | BB / eq partitioning |
| test\_add\_product\_invalid\_sale\_id | POST/sales/{sale\_id}/items | API | BB / boundary |
| test\_add\_product\_invalid\_amount | POST/sales/{sale\_id}/items | API | BB / boundary |
| test\_remove\_product\_success | DELETE/sales/{sale\_id}/items | API | BB / eq partitioning |
| test\_remove\_product\_invalid\_sale\_id | DELETE/sales/{sale\_id}/items | API | BB / boundary |
| test\_remove\_product\_invalid\_amount | DELETE/sales/{sale\_id}/items | API | BB / boundary |
| test\_apply\_discount\_success | PATCH/sales/{sale\_id}/discount | API | BB / eq partitioning |
| test\_apply\_discount\_invalid\_rate | PATCH/sales/{sale\_id}/discount | API | BB / boundary |
| test\_apply\_product\_discount\_success | PATCH/sales/{sale\_id}/items/{product\_barcode}/discount | API | BB / eq partitioning |
| test\_apply\_product\_discount\_invalid\_rate | PATCH/sales/{sale\_id}/items/{product\_barcode}/discount | API | BB / boundary |
| test\_apply\_product\_discount\_invalid\_sale\_id | PATCH/sales/{sale\_id}/items/{product\_barcode}/discount | API | BB / boundary |
| test\_close\_sale\_success | PATCH/sales/{sale\_id}/close | API | BB / eq partitioning |
| test\_close\_sale\_invalid\_id | PATCH/sales/{sale\_id}/close | API | BB / boundary |
| test\_close\_sale\_unauthorized | PATCH/sales/{sale\_id}/close | API | BB / eq partitioning |
| test\_pay\_sale\_success | PATCH/sales/{sale\_id}/pay | API | BB / eq partitioning |
| test\_pay\_sale\_invalid\_cash | PATCH/sales/{sale\_id}/pay | API | BB / boundary |
| test\_get\_sale\_points\_success | GET/sales/{sale\_id}/points | API | BB / eq partitioning |
| test\_get\_sale\_points\_invalid\_id | GET/sales/{sale\_id}/points | API | BB / boundary |

**Sale Integration Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| ----- | :---: | :---: | :---: |
| test\_start\_sale\_success | SaleController.start\_sale() | Integration | BB / eq partitioning |
| test\_list\_sales\_success | SaleController.list\_sales() | Integration | BB / eq partitioning |
| test\_get\_sale\_success | SaleController.get\_sale() | Integration | BB / eq partitioning |
| test\_get\_sale\_not\_found | SaleController.get\_sale() | Integration | BB / eq partitioning |
| test\_delete\_sale\_success | SaleController.delete\_sale() | Integration | BB / eq partitioning |
| test\_delete\_sale\_not\_found | SaleController.delete\_sale() | Integration | BB / eq partitioning |
| test\_add\_product\_success | SaleController.add\_product\_to\_sale() | Integration | BB / eq partitioning |
| test\_add\_product\_bad\_amount | SaleController.add\_product\_to\_sale() | Integration | BB / boundary |
| test\_add\_product\_insufficient\_stock | SaleController.add\_product\_to\_sale() | Integration | BB / eq partitioning |
| test\_remove\_product\_success | SaleController.remove\_product\_from\_sale() | Integration | BB / eq partitioning |
| test\_remove\_product\_bad\_amount | SaleController.remove\_product\_from\_sale() | Integration | BB / boundary |
| test\_remove\_product\_too\_many | SaleController.remove\_product\_from\_sale() | Integration | BB / eq partitioning |
| test\_discount\_sale\_success | SaleController.apply\_discount() | Integration | BB / eq partitioning |
| test\_discount\_sale\_bad\_rate | SaleController.apply\_discount() | Integration | BB / boundary |
| test\_discount\_sale\_not\_open | SaleController.apply\_discount() | Integration | BB / state transition |
| test\_discount\_product\_success | SaleController.apply\_product\_discount() | Integration | BB / eq partitioning |
| test\_discount\_product\_bad\_rate | SaleController.apply\_product\_discount() | Integration | BB / boundary |
| test\_close\_success\_sets\_pending\_and\_closed\_at | SaleController.close\_sale() | Integration | BB / state transition |
| test\_close\_empty\_sale\_deletes\_it | SaleController.close\_sale() | Integration | BB / eq partitioning |
| test\_pay\_success | SaleController.pay\_sale() | Integration | BB / eq partitioning |
| test\_pay\_bad\_cash\_amount | SaleController.pay\_sale() | Integration | BB / boundary |
| test\_pay\_not\_pending | SaleController.pay\_sale() | Integration | BB / state transition |
| test\_points\_success | SaleController.get\_sale\_points() | Integration | BB / eq partitioning |
| test\_points\_not\_paid | SaleController.get\_sale\_points() | Integration | BB / state transition |

**Sale Unit Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| ----- | :---: | :---: | :---: |
| test\_sale\_repo\_create\_sale\_success | SaleRepository.create\_sale() | Unit | BB / eq partitioning |
| test\_sale\_repo\_list\_sales\_returns\_list | SaleRepository.list\_sales() | Unit | BB / eq partitioning |
| test\_sale\_repo\_get\_sale\_not\_found | SaleRepository.get\_sale() | Unit | BB / eq partitioning |
| test\_sale\_repo\_get\_sale\_pending\_no\_lines\_is\_considered\_cancelled | SaleRepository.get\_sale() | Unit | WB / statement |
| test\_sale\_repo\_delete\_sale\_not\_found | SaleRepository.delete\_sale() | Unit | BB / eq partitioning |
| test\_sale\_repo\_delete\_paid\_sale\_conflict | SaleRepository.delete\_sale() | Unit | BB / state transition |
| test\_sale\_repo\_delete\_sale\_restores\_stock\_quantities | SaleRepository.delete\_sale() | Unit | BB / eq partitioning |
| test\_sale\_repo\_add\_product\_bad\_amount | SaleRepository.add\_product\_to\_sale() | Unit | BB / boundary |
| test\_sale\_repo\_add\_product\_sale\_not\_found | SaleRepository.add\_product\_to\_sale() | Unit | BB / eq partitioning |
| test\_sale\_repo\_add\_product\_wrong\_status | SaleRepository.add\_product\_to\_sale() | Unit | BB / state transition |
| test\_sale\_repo\_add\_product\_product\_not\_found | SaleRepository.add\_product\_to\_sale() | Unit | BB / eq partitioning |
| test\_sale\_repo\_add\_product\_insufficient\_stock\_conflict | SaleRepository.add\_product\_to\_sale() | Unit | BB / eq partitioning |
| test\_sale\_repo\_add\_product\_success\_decreases\_stock\_and\_creates\_line | SaleRepository.add\_product\_to\_sale() | Unit | BB / eq partitioning |
| test\_sale\_repo\_remove\_product\_bad\_amount | SaleRepository.remove\_product\_from\_sale() | Unit | BB / boundary |
| test\_sale\_repo\_remove\_product\_sale\_not\_found | SaleRepository.remove\_product\_from\_sale() | Unit | BB / eq partitioning |
| test\_sale\_repo\_remove\_product\_wrong\_status | SaleRepository.remove\_product\_from\_sale() | Unit | BB / state transition |
| test\_sale\_repo\_remove\_product\_line\_not\_found | SaleRepository.remove\_product\_from\_sale() | Unit | BB / eq partitioning |
| test\_sale\_repo\_remove\_product\_success\_partial\_restores\_stock\_and\_decreases\_line\_qty | SaleRepository.remove\_product\_from\_sale() | Unit | BB / eq partitioning |
| test\_sale\_repo\_remove\_product\_deletes\_line\_when\_amount\_eq\_line\_qty | SaleRepository.remove\_product\_from\_sale() | Unit | BB / boundary |
| test\_sale\_repo\_remove\_product\_fails\_when\_amount\_gt\_line\_qty | SaleRepository.remove\_product\_from\_sale() | Unit | BB / eq partitioning |
| test\_sale\_repo\_apply\_discount\_invalid\_rate | SaleRepository.apply\_discount() | Unit | BB / boundary |
| test\_sale\_repo\_apply\_discount\_wrong\_status | SaleRepository.apply\_discount() | Unit | BB / state transition |
| test\_sale\_repo\_apply\_product\_discount\_line\_not\_found | SaleRepository.apply\_product\_discount() | Unit | BB / eq partitioning |
| test\_sale\_repo\_close\_sale\_wrong\_status | SaleRepository.close\_sale() | Unit | BB / state transition |
| test\_sale\_repo\_pay\_sale\_wrong\_state | SaleRepository.pay\_sale() | Unit | BB / state transition |
| test\_sale\_repo\_pay\_sale\_insufficient\_cash | SaleRepository.pay\_sale() | Unit | BB / eq partitioning |
| test\_sale\_repo\_pay\_sale\_success\_updates\_status\_and\_balance | SaleRepository.pay\_sale() | Unit | BB / eq partitioning |
| test\_sale\_repo\_get\_points\_wrong\_state | SaleRepository.get\_sale\_points() | Unit | BB / state transition |
| test\_sale\_repo\_get\_points\_success\_equals\_floor\_total | SaleRepository.get\_sale\_points() | Unit | BB / boundary |
| test\_sale\_repo\_apply\_product\_discount\_invalid\_rate\_raises | SaleRepository.apply\_product\_discount() | Unit | BB / boundary |
| test\_sale\_repo\_pay\_sale\_invalid\_cash\_amount\_raises | SaleRepository.pay\_sale() | Unit | BB / boundary |
| test\_sale\_repo\_apply\_discount\_success\_updates\_sale | SaleRepository.apply\_discount() | Unit | BB / eq partitioning |
| test\_sale\_repo\_apply\_product\_discount\_success\_updates\_line | SaleRepository.apply\_product\_discount() | Unit | BB / eq partitioning |
| test\_sale\_repo\_close\_empty\_sale\_deletes\_sale | SaleRepository.close\_sale() | Unit | BB / eq partitioning |
| test\_sale\_repo\_pay\_sale\_sets\_closed\_at\_if\_missing | SaleRepository.pay\_sale() | Unit | WB / statement |
| test\_sale\_repo\_pay\_sale\_creates\_system\_info\_if\_missing | SaleRepository.pay\_sale() | Unit | WB / statement |
| test\_sale\_repo\_apply\_product\_discount\_wrong\_status\_raises | SaleRepository.apply\_product\_discount() | Unit | BB / state transition |

**Accounting API Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| ----- | :---: | :---: | :---: |
| test\_get\_balance\_success\_as\_admin | GET /api/v1/balance | API | BB / Equivalence Partitioning |
| test\_get\_balance\_forbidden\_as\_manager | GET /api/v1/balance | API | BB / Role-Based Analysis |
| test\_get\_balance\_unauthenticated | GET /api/v1/balance | API | BB / Negative Testing |
| test\_set\_balance\_success | POST /api/v1/balance/set | API | BB / Equivalence Partitioning |
| test\_set\_balance\_negative\_amount | POST /api/v1/balance/set | API | BB / Boundary Value Analysis |
| test\_reset\_balance\_success | POST /api/v1/balance/reset | API | BB / State Transition |

**Accounting Integration Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| ----- | :---: | :---: | :---: |
| test\_validation\_get\_history\_invalid\_date\_range | AccountingController.get\_history | Integration | Gray Box / Error Path |
| test\_controller\_record\_transaction\_success | AccountingController.record\_transaction | Integration | Gray Box / Success Path |
| test\_controller\_get\_history\_success | AccountingController.get\_history | Integration | Gray Box / Data Flow |
| test\_accounting\_service\_coverage | AccountingService.record\_transaction | Integration | Gray Box / Component Integration |

**Accounting Unit Tests**

| Test case name | Object(s) tested | Test level | Technique used |
| ----- | :---: | :---: | :---: |
| test\_repository\_coverage\_edge\_cases | TransactionRepository (session injection) | Unit | WB / Statement Coverage |
| test\_repository\_coverage\_edge\_cases | TransactionRepository (set\_balance) | Unit | WB / Branch Coverage |
| test\_validation\_transaction\_negative\_amount | TransactionCreateDTO | Unit | WB / Boundary Value |
| test\_validation\_transaction\_zero\_amount | TransactionCreateDTO | Unit | WB / Boundary Value |

# Coverage

## Coverage of FR

| Functional Requirement or scenario | Test(s) |
| :---- | ----- |
| FR3.1 | **Define a new product type product\_test.py:** test\_create\_product\_success\_all\_roles test\_create\_product\_success\_as\_admin test\_create\_product\_success\_as\_manager test\_create\_product\_minimal\_fields **product\_repository\_test.py** test\_create\_product\_success test\_create\_product\_minimal  **Modify a new product type product\_route\_test.py:** test\_update\_product\_success test\_update\_product\_not\_found test\_update\_product\_barcode\_conflict **product\_repository\_test.py:** test\_update\_product\_all\_fields test\_update\_product\_partial test\_update\_product\_not\_found **product\_controller\_test.py:** test\_update\_product  |
| FR3.2 | **product\_route\_test.py:** test\_delete\_product\_success  test\_delete\_product\_not\_found test\_delete\_product\_forbidden\_as\_cashier test\_delete\_product\_unauthenticated **product\_repository\_test.py:** test\_delete\_product\_success test\_delete\_product\_not\_found **product\_controller\_test.py:** test\_delete\_product |
| FR3.3 | **product\_route\_test.py:** test\_get\_all\_products\_success\_as\_admin test\_get\_all\_products\_success\_as\_manager test\_get\_all\_products\_success\_as\_cashier test\_get\_all\_products\_unauthenticated **product\_repository\_test.py:** test\_get\_all\_products\_empty test\_get\_all\_products\_success **product\_controller\_test.py:** test\_get\_all\_products |
| FR3.4 | **Search by barcode product\_route\_test.py:** test\_get\_product\_by\_barcode\_success test\_get\_product\_by\_barcode\_not\_found test\_get\_product\_by\_barcode\_invalid\_format **product\_repository\_test.py:** test\_get\_product\_by\_barcode\_success test\_get\_product\_by\_barcode\_not\_found **product\_controller\_test.py:** test\_get\_product\_by\_barcode **Search by description product\_route\_test.py:** test\_search\_products\_success test\_search\_products\_no\_results test\_search\_products\_case\_insensitive **product\_repository\_test.py:** test\_search\_products\_by\_description\_found test\_search\_products\_by\_description\_not\_found test\_search\_products\_case\_insensitive **product\_controller\_test.py:** test\_search\_products\_by\_description |
| FR4.1 | **product\_controller\_test.py:** test\_update\_quantity **product\_repository\_test.py:** test\_update\_quantity\_increase test\_update\_quantity\_decrease test\_update\_quantity\_to\_zero test\_update\_quantity\_negative\_result test\_update\_quantity\_not\_found **product\_test.py:** test\_update\_quantity\_e2e |
| FR4.2 | **product\_controller\_test.py:** test\_update\_position **product\_repository\_test.py:** test\_update\_position\_valid\_format test\_update\_position\_various\_formats test\_update\_position\_invalid\_forma test\_update\_position\_clear test\_update\_position\_not\_found **product\_test.py:** test\_update\_position\_e2e |
| FR4.3 | **order\_repository\_test.py:** test\_issue\_reorder\_warning\_success **order\_controller.py:** issue\_reorder\_warning  **order\_repository.py:** issue\_reorder\_warning **order\_route.py (API):** POST /orders/reorder  |
| FR4.4 | **order\_route\_test.py:** test\_create\_order\_success\_as\_admin test\_create\_order\_success\_as\_manager test\_create\_order\_invalid\_product test\_create\_order\_missing\_fields test\_create\_order\_invalid\_quantity test\_create\_order\_unauthenticated test\_create\_order\_forbidden\_as\_cashier test\_pay\_order\_success test\_pay\_order\_wrong\_status test\_pay\_order\_not\_found test\_payfor\_order\_success\_as\_admin test\_payfor\_order\_success\_as\_manager test\_payfor\_order\_forbidden\_as\_cashier test\_payfor\_order\_unauthenticated **order\_repository\_test.py:** test\_create\_order\_success test\_pay\_order\_success test\_pay\_order\_wrong\_status test\_pay\_order\_insufficient\_balance **order\_controller\_test.py:** test\_create\_order test\_pay\_order test\_create\_and\_pay\_order **order\_test.py:** test\_create\_and\_pay\_order\_e2e test\_create\_and\_pay\_order\_insufficient\_balance\_e2e |
| FR4.5 | **order\_repository\_test.py:** test\_pay\_reorder\_warning\_success test\_pay\_reorder\_warning\_not\_found test\_pay\_reorder\_warning\_not\_a\_reorder test\_pay\_reorder\_warning\_already\_paid test\_pay\_reorder\_warning\_insufficient\_balance **order\_controller.py:** pay\_reorder\_warning **order\_repository.py:** pay\_reorder\_warning **order\_route.py (API):** PATCH /orders/{order\_id}/pay-reorder |
| FR4.6 | **order\_route\_test.py:** test\_record\_arrival\_success test\_record\_arrival\_wrong\_status test\_record\_arrival\_not\_found test\_record\_arrival\_product\_without\_position **order\_repository\_test.py:** test\_record\_order\_arrival\_success test\_record\_arrival\_wrong\_status test\_record\_arrival\_no\_position test\_record\_arrival\_orphaned\_order **order\_controller\_test.py:** test\_record\_order\_arrival |
| FR4.7 | **order\_route\_test.py:** test\_get\_all\_orders\_success\_as\_admin test\_get\_all\_orders\_success\_as\_manager test\_get\_all\_orders\_forbidden\_as\_cashier test\_get\_all\_orders\_unauthenticated **order\_repository\_test.py:** test\_get\_all\_orders\_empty test\_get\_all\_orders\_success **order\_controller\_test.py:** test\_get\_all\_orders |
| FR5.1 | **customer\_test.py: Create customer** test\_create\_customer\_success\_as\_admin test\_create\_customer\_success\_as\_manager test\_create\_customer\_success\_as\_cashier test\_create\_customer\_conflict test\_create\_customer\_missing\_fields test\_create\_customer\_unauthenticated **Update a customer** test\_update\_customer\_name\_but\_not\_card\_success test\_update\_customer\_card\_but\_not\_name\_success test\_update\_customer\_deletion\_card\_success test\_update\_customer\_not\_found test\_update\_customer\_card\_not\_found test\_update\_customer\_name\_conflict test\_update\_customer\_unauthenticated **cusotmer\_route\_test.py: Create customer** test\_create\_customer\_success test\_create\_customer\_bad\_request **Update a customer** test\_update\_customer\_success test\_update\_customer\_invalid\_id test\_update\_customer\_invalid\_payload test\_update\_customer\_not\_found **customer\_controller\_test.py: Create customer** test\_create\_customer\_without\_card test\_create\_customer\_with\_card **Update a customer** test\_update\_customer\_name\_and\_card test\_update\_customer\_name\_and\_card\_customer\_not\_found **customer\_repository\_test.py: Create customer** test\_create\_customer\_success test\_create\_customer\_conflict **Update a customer** test\_update\_customer\_card\_success test\_update\_customer\_card\_customer\_not\_found test\_update\_customer\_card\_loyalty\_card\_not\_found test\_update\_customer\_card\_already\_attached\_to\_him test\_update\_customer\_card\_already\_attached\_to\_other test\_update\_customer\_only\_name\_success test\_update\_customer\_only\_name\_not\_found test\_update\_customer\_only\_name\_conflict\_on\_name test\_update\_customer\_only\_card\_success test\_update\_customer\_detach\_card\_success |
| FR5.2 | **customer\_test.py:** test\_delete\_customer\_success test\_delete\_customer\_unauthenticated test\_delete\_customer\_not\_found **customer\_route\_test.py:** test\_delete\_customer\_success test\_delete\_customer\_not\_found **customer\_controller\_test.py:** test\_delete\_customer test\_delete\_customer\_not\_found **customer\_repository\_test.py:** test\_delete\_customer\_success test\_delete\_customer\_not\_found |
| FR5.3 | **customer\_test.py:** test\_get\_customer\_success test\_get\_customer\_not\_found test\_get\_customer\_unauthenticated **customer\_route\_test.py:** test\_get\_customer\_success test\_get\_customer\_invalid\_id test\_get\_customer\_not\_found **customer\_controller\_test.py:** test\_get\_customer test\_get\_customer\_not\_found **customer\_repository\_test.py:** test\_get\_customer\_success test\_get\_customer\_not\_found |
| FR5.4 | **customer\_test.py:** test\_list\_customers\_success\_as\_admin test\_list\_customers\_success\_as\_manager test\_list\_customers\_success\_as\_cashier test\_list\_customers\_unauthenticated **customer\_route\_test.py:** test\_get\_all\_customers\_success **customer\_controller\_test.py:** test\_list\_customers test\_list\_customers\_empty **customer\_repository\_test.py:** test\_list\_customers\_success test\_list\_customers\_empty |
| FR5.5 | **customer\_test.py:** test\_create\_loyalty\_card\_success\_as\_admin test\_create\_loyalty\_card\_success\_as\_manager test\_create\_loyalty\_card\_success\_as\_cashier test\_create\_loyalty\_card\_unauthenticated **customer\_route\_test.py:** test\_create\_loyalty\_card\_success **customer\_controller\_test.py:** test\_create\_loyalty\_card **customer\_repository\_test.py:** test\_create\_loyalty\_card\_success |
| FR5.6 | **customer\_test.py:** test\_attach\_loyalty\_card\_to\_customer\_success test\_attach\_loyalty\_card\_to\_customer\_customer\_not\_found test\_attach\_loyalty\_card\_to\_customer\_card\_not\_found test\_attach\_loyalty\_card\_to\_customer\_already\_attached\_to\_this\_customer test\_attach\_loyalty\_card\_to\_customer\_already\_attached\_to\_other\_customer test\_attach\_loyalty\_card\_to\_customer\_unauthenitcated **customer\_route\_test.py:** test\_attach\_loyalty\_card\_to\_customer\_success test\_attach\_card\_not\_found\_error test\_attach\_card\_conflict\_error **customer\_controller\_test.py:** test\_attach\_loyalty\_card\_to\_customer test\_attach\_loyalty\_card\_to\_customer\_customer\_not\_found |
| FR5.7 | **customer\_test.py:** test\_update\_loyalty\_card\_points\_success test\_update\_loyalty\_card\_points\_card\_not\_found test\_update\_loyalty\_card\_points\_unauthenticated **customer\_route\_test.py:** test\_update\_loyalty\_card\_points\_success **customer\_controller\_test.py:** test\_update\_loyalty\_card\_points test\_update\_loyalty\_card\_points\_not\_found **customer\_repository\_test.py:** test\_update\_loyalty\_card\_points\_success test\_update\_loyalty\_card\_points\_not\_enough\_points test\_update\_loyalty\_card\_points\_not\_found |
| FR6.1 | **sales\_test.py:** test\_start\_sale\_success\_as\_admin test\_start\_sale\_success\_as\_cashier test\_start\_sale\_unauthenticated **sale\_route\_test.py:** test\_start\_sale\_success test\_start\_sale\_unauthorized **sale\_controller\_test.py:** test\_start\_sale\_success **sale\_repository\_test.py:** test\_sale\_repo\_create\_sale\_success |
| FR6.2 | **sales\_test.py:** test\_add\_item\_to\_sale\_success test\_add\_item\_invalid\_amount test\_add\_item\_sale\_not\_found test\_add\_item\_invalid\_status test\_add\_item\_unauthenticated **sale\_route\_test.py:** test\_add\_product\_success test\_add\_product\_invalid\_sale\_id test\_add\_product\_invalid\_amount **sale\_controller\_test.py:** test\_add\_product\_success test\_add\_product\_bad\_amount test\_add\_product\_insufficient\_stock **sale\_repository\_test.py:** test\_sale\_repo\_add\_product\_success\_decreases\_stock\_and\_creates\_line test\_sale\_repo\_add\_product\_bad\_amount test\_sale\_repo\_add\_product\_sale\_not\_found test\_sale\_repo\_add\_product\_wrong\_status test\_sale\_repo\_add\_product\_product\_not\_found test\_sale\_repo\_add\_product\_insufficient\_stock\_conflict |
| FR6.3 | **sales\_test.py:** test\_remove\_item\_from\_sale\_success test\_remove\_item\_invalid\_amount test\_remove\_item\_sale\_not\_found test\_remove\_item\_invalid\_status test\_remove\_item\_not\_in\_sale test\_remove\_item\_unauthenticated **sale\_route\_test.py:** test\_remove\_product\_success test\_remove\_product\_invalid\_sale\_id test\_remove\_product\_invalid\_amount **sale\_controller\_test.py:** test\_remove\_product\_success test\_remove\_product\_bad\_amount test\_remove\_product\_too\_many **sale\_repository\_test.py:** test\_sale\_repo\_remove\_product\_success\_partial\_restores\_stock\_and\_decreases\_line\_qty  test\_sale\_repo\_remove\_product\_deletes\_line\_when\_amount\_eq\_line\_qty test\_sale\_repo\_remove\_product\_fails\_when\_amount\_gt\_line\_qty test\_sale\_repo\_remove\_product\_bad\_amount test\_sale\_repo\_remove\_product\_sale\_not\_found  test\_sale\_repo\_remove\_product\_wrong\_status test\_sale\_repo\_remove\_product\_line\_not\_found |
| FR6.4 | **sales\_test.py:** test\_apply\_discount\_to\_sale\_success test\_apply\_discount\_invalid\_ratetest\_apply\_discount\_to\_sale\_not\_found test\_apply\_discount\_to\_sale\_invalid\_id test\_apply\_discount\_to\_sale\_invalid\_status test\_apply\_discount\_to\_sale\_unauthenticated **sale\_route\_test.py:** test\_apply\_discount\_success test\_apply\_discount\_invalid\_rate **sale\_controller\_test.py:** test\_discount\_sale\_success test\_discount\_sale\_bad\_rate test\_discount\_sale\_not\_open **sale\_repository\_test.py:** test\_sale\_repo\_apply\_discount\_success\_updates\_sale test\_sale\_repo\_apply\_discount\_invalid\_rate test\_sale\_repo\_apply\_discount\_wrong\_status |
| FR6.5 | **sales\_test.py:** test\_apply\_discount\_to\_item\_success test\_apply\_discount\_to\_item\_invalid\_rate test\_apply\_discount\_to\_item\_not\_found test\_apply\_discount\_to\_item\_sale\_not\_found  test\_apply\_discount\_to\_item\_invalid\_status test\_apply\_discount\_to\_item\_unauthenticated  **sale\_route\_test.py:** test\_apply\_product\_discount\_success test\_apply\_product\_discount\_invalid\_rate test\_apply\_product\_discount\_invalid\_sale\_id **sale\_controller\_test.py:** test\_discount\_product\_success test\_discount\_product\_bad\_rate **sale\_repository\_test.py:** test\_sale\_repo\_apply\_product\_discount\_success\_updates\_line test\_sale\_repo\_apply\_product\_discount\_invalid\_rate\_raises test\_sale\_repo\_apply\_product\_discount\_line\_not\_found test\_sale\_repo\_apply\_product\_discount\_wrong\_status\_raises |
| FR6.6 | **sales\_test.py:** test\_get\_points\_success test\_get\_points\_wrong\_state test\_get\_points\_invalid\_id test\_get\_points\_not\_found test\_get\_points\_unauthenticated **sale\_route\_test.py:** test\_get\_sale\_points\_success test\_get\_sale\_points\_invalid\_id **sale\_controller\_test.py:** test\_points\_success test\_points\_not\_paid **sale\_repository\_test.py:** test\_sale\_repo\_get\_points\_success\_equals\_floor\_total test\_sale\_repo\_get\_points\_wrong\_state |
| FR6.10 | **sales\_test.py:** test\_close\_sale\_success test\_close\_sale\_invalid\_id test\_close\_sale\_not\_found test\_close\_sale\_already\_closed  test\_close\_empty\_sale\_deletes\_sale test\_close\_sale\_unauthenticated  **sale\_route\_test.py:** test\_close\_sale\_success test\_close\_sale\_invalid\_id test\_close\_sale\_unauthorized **sale\_controller\_test.py:** test\_close\_success\_sets\_pending\_and\_closed\_at test\_close\_empty\_sale\_deletes\_it **sale\_repository\_test.py:** test\_sale\_repo\_close\_empty\_sale\_deletes\_sale test\_sale\_repo\_close\_sale\_wrong\_status |
| FR6.11 | **Commit sale sales\_test.py:** test\_pay\_sale\_success\_and points test\_pay\_sale\_wrong\_state test\_pay\_sale\_invalid\_cash\_amount test\_pay\_sale\_not\_found test\_pay\_sale\_invalid\_id test\_pay\_sale\_unauthenticated **sale\_route\_test.py:** test\_pay\_sale\_success test\_pay\_sale\_invalid\_cash **sale\_controller\_test.py:** test\_pay\_sale\_success test\_pay\_bad\_cash\_amount test\_pay\_not\_pending **sale\_repository\_test.py:** test\_sale\_repo\_pay\_sale\_wrong\_state test\_sale\_repo\_pay\_sale\_insufficient cash test\_sale\_repo\_pay\_sale\_success\_updates\_status\_and\_balance test\_sale\_repo\_pay\_sale\_sets\_closed\_at\_if\_missing test\_sale\_repo\_pay\_sale\_creates\_system\_info\_if\_missing  **Rollback sale sales\_test.py:** test\_delete\_sale\_success test\_delete\_sale\_bad\_id test\_delete\_sale\_not\_found test\_delete\_sale\_unauthenticated test\_delete\_paid\_sale\_cannot\_be\_deleted **sale\_route\_test.py:** test\_delete\_sale\_success test\_delete\_sale\_invalid\_id **sale\_controller\_test.py:** test\_delete\_sale\_success test\_delete\_sale\_not\_found **sale\_repository\_test.py:** test\_sale\_repo\_delete\_sale\_not\_found test\_sale\_repo\_delete\_paid\_sale\_conflict test\_sale\_repo\_delete\_sale\_restores\_stock\_quantities |
| FR6.12 | **return\_route\_test.py:**  test\_start\_return\_route,  test\_start\_return\_route\_sale\_not\_found  **return\_controller\_test.py:**  test\_start\_return,  **return\_repository\_test.py:**  test\_create\_and\_get\_returns\_also\_with\_invalid\_sale\_state |
| FR6.13 | **return\_route\_test.py:**  test\_add\_product\_to\_return\_route,  test\_add\_product\_to\_return\_route\_not\_found,  test\_delete\_product\_from\_return\_route,  test\_delete\_product\_from\_return\_route\_not\_found **return\_controller\_test.py:**  test\_add\_product\_to\_return\_success,  test\_add\_product\_to\_return\_not\_found,  test\_add\_product\_to\_return\_invalid\_state,  test\_remove\_product\_from\_return\_success,  test\_remove\_product\_from\_return\_not\_found,  test\_remove\_product\_from\_return\_invalid\_state **return\_repository\_test.py:**  test\_add\_and\_remove\_line\_all\_cases |
| FR6.14 | **return\_route\_test.py:**  test\_close\_return\_route,  test\_close\_return\_route\_not\_found,  **return\_controller\_test.py:**  test\_close\_return\_success,  test\_close\_return\_fail\_if\_not\_open,  test\_close\_return\_not\_found,  test\_close\_empty\_return\_with\_deletion,  **return\_repository\_test.py:**  test\_update\_status |
| FR6.15 | **return\_route\_test.py:**  test\_delete\_return\_route,  test\_delete\_return\_route\_not\_found **return\_controller\_test.py:**  test\_delete\_return\_success,  test\_delete\_return\_not\_found,  test\_delete\_return\_fail\_if\_reimbursed **return\_repository\_test.py:**  test\_update\_status |
| FR7.1 | **sales\_test.py:** test\_pay\_sale\_success test\_pay\_sale\_wrong\_state test\_pay\_sale\_invalid\_cash\_amount test\_pay\_sale\_not\_found test\_pay\_sale\_invalid\_id test\_pay\_sale\_unauthenticated **sale\_route\_test.py:** test\_pay\_sale\_success test\_pay\_sale\_invalid\_cash **sale\_controller\_test.py:** test\_pay\_success test\_pay\_bad\_cash\_amount test\_pay\_not\_pending **sale\_repository\_test.py:** test\_sale\_repo\_pay\_sale\_wrong\_state test\_sale\_repo\_pay\_sale\_insufficient\_cash test\_sale\_repo\_pay\_sale\_success\_updates\_status\_and\_balance test\_sale\_repo\_pay\_sale\_invalid\_cash\_amount\_raises test\_sale\_repo\_pay\_sale\_sets\_closed\_at\_if\_missing test\_sale\_repo\_pay\_sale\_creates\_system\_info\_if\_missing |
| FR7.3 | **return\_route\_test.py:**  test\_reimburse\_return\_route,  test\_reimburse\_return\_route\_not\_found **return\_controller\_test.py:**  test\_reimburse\_return\_success,  test\_reimburse\_return\_not\_found,  test\_reimburse\_return\_invalid\_state **return\_repository\_test.py:**  test\_update\_status |
| FR7.4 | **return\_route\_test.py:**  test\_reimburse\_return\_route,  test\_reimburse\_return\_route\_not\_found **return\_controller\_test.py:**  test\_reimburse\_return\_success,  test\_reimburse\_return\_not\_found,  test\_reimburse\_return\_invalid\_state **return\_repository\_test.py:**  test\_update\_status |
| FR8.1 | **accounting\_controller\_test.py:** test\_account\_service\_coverage |
| FR8.2 | **accounting\_test.py:** test\_validation\_transaction\_negative\_amount test\_validation\_transaction\_zero\_amount **accounting\_controller\_test.py:** test\_controller\_record\_transaction\_success **accounting\_repository\_test.py:** test\_repository\_coverage\_edge\_cases |
| FR8.3 | **accounting\_controller\_test.py:** test\_controller\_get\_history\_success **accounting\_repository\_test.py:** test\_repository\_coverage\_edge\_cases |
| FR8.4 | **accounting\_controller\_test.py:** test\_accounting\_service\_coverage **accounting\_repository\_test.py:** test\_repository\_coverage\_edge\_cases |
| Sc 1-1 \- Create product type X | **product\_test.py:** test\_create\_product\_success\_as\_admin test\_create\_product\_success\_as\_manager test\_create\_product\_minimal\_fields **product\_repository\_test.py:** test\_create\_product\_success test\_create\_product\_minimal |
| Sc 1-2 \- Modify location | **product\_controller\_test.py:** test\_update\_position **product\_repository\_test.py:** test\_update\_position\_valid\_format test\_update\_position\_invalid\_forma test\_update\_position\_clear |
| Sc 1-3 \- Modify price | **product\_route\_test.py:** test\_update\_product\_success **product\_repository\_test.py:** test\_update\_product\_all\_fields |
| Sc 3-1 \- Order issued | **order\_route\_test.py:** test\_create\_order\_success\_as\_admin test\_create\_order\_success\_as\_manager test\_create\_order\_invalid\_product test\_create\_order\_missing\_fields test\_create\_order\_invalid\_quantity **order\_repository\_test.py:** test\_create\_order\_success **order\_controller\_test.py:** test\_create\_order |
| Scenario 3-2 – Order of product type X payed | **order\_route\_test.py:** test\_pay\_order\_success test\_pay\_order\_wrong\_status test\_pay\_order\_not\_found test\_payfor\_order\_success\_as\_admin test\_payfor\_order\_success\_as\_manager **order\_repository\_test.py:** test\_pay\_order\_success test\_pay\_order\_wrong\_status test\_pay\_order\_insufficient\_balance **order\_controller\_test.py:** test\_pay\_order test\_create\_and\_pay\_order |
| Scenario 3-3 – Record order arrival  | **order\_route\_test.py:** test\_record\_arrival\_success test\_record\_arrival\_wrong\_status test\_record\_arrival\_not\_found test\_record\_arrival\_product\_without\_position **order\_repository\_test.py:** test\_record\_order\_arrival\_success test\_record\_arrival\_wrong\_status test\_record\_arrival\_no\_position test\_record\_arrival\_orphaned\_orde **order\_controller\_test.py:** test\_record\_order\_arrival  |
| Sc 4-1 \- Create customer record | **customer\_test.py:** test\_create\_customer\_success\_as\_admin test\_create\_customer\_success\_as\_manager test\_create\_customer\_success\_as\_cashier **customer\_route\_test.py:** test\_create\_customer\_success **customer\_controller\_test.py:** test\_create\_customer\_without\_card **customer\_repository\_test.py:** test\_create\_customer\_success |
| Sc 4-2 \- Attach Loyalty card to customer record | **customer\_test.py:** test\_create\_loyalty\_card\_success\_as\_admin test\_create\_loyalty\_card\_success\_as\_manager test\_create\_loyalty\_card\_success\_as\_cashier test\_attach\_loyalty\_card\_to\_customer\_success **customer\_route\_test.py:** test\_create\_loyalty\_card\_success test\_attach\_loyalty\_card\_to\_customer\_success **customer\_controller\_test.py:** test\_create\_loyalty\_card test\_attach\_loyalty\_card\_to\_customer **customer\_repository\_test.py:** test\_create\_loyalty\_card\_success |
| Sc 4-3 \- Detach Loyalty card from customer record | **customer\_test.py:** test\_get\_customer\_success test\_update\_customer\_deletion\_card\_success **customer\_route\_test.py:** test\_get\_customer\_success **customer\_controller\_test.py:** test\_get\_customer **customer\_repository\_test.py:** test\_get\_customer\_success test\_update\_customer\_detach\_card\_success |
| Sc 4-4 \- Update customer record | **customer\_test.py:** test\_get\_customer\_success test\_update\_customer\_name\_but\_not\_card\_success test\_update\_customer\_card\_but\_not\_name\_success **customer\_route\_test.py:** test\_get\_customer\_success test\_update\_customer\_success **customer\_controller\_test.py:** test\_get\_customer test\_update\_customer\_name\_and\_card **customer\_repository\_test.py:** test\_get\_customer\_success test\_update\_customer\_only\_name\_success test\_update\_customer\_only\_card\_success |
| Sc 6.1 Sale of product type X completed | **sales\_test.py:** test\_start\_sale\_success\_as\_admin test\_start\_sale\_success\_as\_cashier test\_add\_item\_to\_sale\_success test\_close\_sale\_success test\_pay\_sale\_success\_and points **sale\_route\_test.py:** test\_start\_sale\_success test\_add\_product\_success test\_close\_sale\_success test\_pay\_sale\_success **sale\_controller\_test.py:** test\_start\_sale\_success test\_add\_product\_success test\_close\_success\_sets\_pending\_and\_closed\_at test\_pay\_sale\_success **sale\_repository\_test.py:** test\_sale\_repo\_create\_sale\_success test\_sale\_repo\_add\_product\_success\_decreases\_stock\_and\_creates\_line test\_sale\_repo\_pay\_sale\_success\_updates\_status\_and\_balance |
| Sc 6.2 Sale of product type X with product discount | **sales\_test.py:** test\_start\_sale\_success\_as\_admin test\_start\_sale\_success\_as\_cashier test\_add\_item\_to\_sale\_success test\_apply\_discount\_to\_item\_success test\_close\_sale\_success test\_pay\_sale\_success\_and points **sale\_route\_test.py:** test\_start\_sale\_success test\_add\_product\_success test\_apply\_product\_discount\_success test\_close\_sale\_success test\_pay\_sale\_success **sale\_controller\_test.py:** test\_start\_sale\_success test\_add\_product\_success test\_discount\_product\_success test\_close\_success\_sets\_pending\_and\_closed\_at test\_pay\_sale\_success **sale\_repository\_test.py:** test\_sale\_repo\_create\_sale\_success test\_sale\_repo\_add\_product\_success\_decreases\_stock\_and\_creates\_line test\_sale\_repo\_apply\_product\_discount\_success\_updates\_line test\_sale\_repo\_pay\_sale\_success\_updates\_status\_and\_balance |
| Sc 6.3 Sale of product type X with sale discount | **sales\_test.py:** test\_start\_sale\_success\_as\_admin test\_start\_sale\_success\_as\_cashier test\_add\_item\_to\_sale\_success test\_apply\_discount\_to\_sale\_success test\_close\_sale\_success test\_pay\_sale\_success\_and points **sale\_route\_test.py:** test\_start\_sale\_success test\_add\_product\_success test\_apply\_discount\_success test\_close\_sale\_success test\_pay\_sale\_success **sale\_controller\_test.py:** test\_start\_sale\_success test\_add\_product\_success test\_discount\_sale\_success test\_close\_success\_sets\_pending\_and\_closed\_at test\_pay\_sale\_success **sale\_repository\_test.py:** test\_sale\_repo\_create\_sale\_success test\_sale\_repo\_add\_product\_success\_decreases\_stock\_and\_creates\_line test\_sale\_repo\_apply\_discount\_success\_updates\_sale test\_sale\_repo\_pay\_sale\_success\_updates\_status\_and\_balance |
| Sc 6.4 Sale of product type X with Loyalty Card update | **sales\_test.py:** test\_start\_sale\_success\_as\_admin test\_start\_sale\_success\_as\_cashier test\_add\_item\_to\_sale\_success test\_close\_sale\_success test\_pay\_sale\_success\_and points test\_get\_points\_success **sale\_route\_test.py:** test\_start\_sale\_success test\_add\_product\_success test\_close\_sale\_success test\_pay\_sale\_success test\_get\_sale\_points\_success **sale\_controller\_test.py:** test\_start\_sale\_success test\_add\_product\_success test\_close\_success\_sets\_pending\_and\_closed\_at test\_pay\_sale\_success test\_points\_success **sale\_repository\_test.py:** test\_sale\_repo\_create\_sale\_success test\_sale\_repo\_add\_product\_success\_decreases\_stock\_and\_creates\_line test\_sale\_repo\_pay\_sale\_success\_updates\_status\_and\_balance test\_sale\_repo\_get\_points\_success\_equals\_floor\_total |
| Sc 6.5 Sale of product type X cancelled | **sales\_test.py:** test\_start\_sale\_success\_as\_admin test\_start\_sale\_success\_as\_cashier test\_add\_item\_to\_sale\_success test\_close\_sale\_success test\_delete\_sale\_success **sale\_route\_test.py:** test\_start\_sale\_success test\_add\_product\_success test\_close\_sale\_success test\_delete\_sale\_success **sale\_controller\_test.py:** test\_start\_sale\_success test\_add\_product\_success test\_close\_success\_sets\_pending\_and\_closed\_at test\_delete\_sale\_success **sale\_repository\_test.py:** test\_sale\_repo\_create\_sale\_success test\_sale\_repo\_add\_product\_success\_decreases\_stock\_and\_creates\_line test\_sale\_repo\_delete\_sale\_restores\_stock\_quantities |
| Sc 6.6 Sale of product type X completed (Cash) | **sales\_test.py:** test\_start\_sale\_success\_as\_admin test\_start\_sale\_success\_as\_cashier test\_add\_item\_to\_sale\_success test\_close\_sale\_success test\_pay\_sale\_success\_and points **sale\_route\_test.py:** test\_start\_sale\_success test\_add\_product\_success test\_close\_sale\_success test\_pay\_sale\_success **sale\_controller\_test.py:** test\_start\_sale\_success test\_add\_product\_success test\_close\_success\_sets\_pending\_and\_closed\_at test\_pay\_sale\_success **sale\_repository\_test.py:** test\_sale\_repo\_create\_sale\_success test\_sale\_repo\_add\_product\_success\_decreases\_stock\_and\_creates\_line test\_sale\_repo\_pay\_sale\_success\_updates\_status\_and\_balance |
| Sc 7.4 Manage cash payment | **sales\_test.py:** test\_pay\_sale\_success\_and points **sale\_route\_test.py:** test\_pay\_sale\_success **sale\_controller\_test.py:** test\_pay\_sale\_success **sale\_repository\_test.py:** test\_sale\_repo\_pay\_sale\_success\_updates\_status\_and\_balance |
| Sc 8-2 Return transaction of product type X completed, cash | **return\_route\_test.py:**  test\_start\_return\_route  test\_add\_product\_to\_return\_route  test\_close\_return\_route  test\_reimburse\_return\_route  **return\_controller\_test.py:**  test\_start\_return  test\_add\_product\_to\_return\_success  test\_close\_return\_success  test\_reimburse\_return\_success **return\_repository\_test.py:**  test\_create\_and\_get\_returns\_also\_with\_invalid\_sale\_state  test\_add\_and\_remove\_line\_all\_cases test\_update\_status |
| Sc 9-1 List credits and debits | **accounting\_controller\_test.py:** test\_controller\_get\_history\_success **accounting\_repository\_test.py:** test\_repository\_coverage\_edge\_cases |
| Sc 10-2 \- Return cash payment  | **return\_route\_test.py:**  test\_start\_return\_route  test\_add\_product\_to\_return\_route  test\_close\_return\_route  test\_reimburse\_return\_route  **return\_controller\_test.py:**  test\_start\_return  test\_add\_product\_to\_return\_success  test\_close\_return\_success  test\_reimburse\_return\_success **return\_repository\_test.py:**  test\_create\_and\_get\_returns\_also\_with\_invalid\_sale\_state  test\_add\_and\_remove\_line\_all\_cases test\_update\_status |

## Coverage white box

Report here the screenshot of coverage values obtained with PyTest  
