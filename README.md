# annotation_workflow_template

This repo holds the current version of the DCML annotation workflow which is pulled by all subcorpus repos upon push to their main branch. 

Please note that the `meta_ corpora` branch should be used with collections of corpora.


# Overview
|file_name|measures|labels|standard|               annotators                | reviewers  |
|---------|-------:|-----:|--------|-----------------------------------------|------------|
|op12n01  |      23|    43|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.30) |Adrian Nagel|
|op12n02  |      79|   125|2.3.0   |Adrian Nagel (2.1.0), John Heilig (2.3.0)|Adrian Nagel|
|op12n03  |      52|   110|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op12n04  |      72|    97|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op12n05  |      40|   109|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op12n06  |      56|   126|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op12n07  |      56|    74|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op12n08  |      32|    78|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op38n01  |      86|   141|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op38n02  |      41|    46|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op38n03  |      48|    87|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op38n04  |      36|    66|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op38n05  |      41|    70|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op38n06  |      47|   104|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op38n07  |      53|    55|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op38n08  |      84|   130|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op43n01  |      42|   102|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op43n02  |      30|    98|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op43n03  |      35|   112|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op43n04  |      36|    52|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op43n05  |      36|   110|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op43n06  |      72|   127|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op47n01  |     184|   158|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op47n02  |     126|   183|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op47n03  |     106|    93|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op47n04  |      38|    21|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op47n05  |      41|   109|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op47n06  |      74|    83|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op47n07  |      97|   147|2.1.1   |Adrian Nagel                             |Adrian Nagel|
|op54n01  |      61|   110|2.1.1   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op54n02  |     159|   286|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op54n03  |     194|   267|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op54n04  |      63|    91|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op54n05  |     204|   118|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op54n06  |      90|   171|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op57n01  |     146|   313|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op57n02  |     125|   183|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op57n03  |      67|   186|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op57n04  |      92|   116|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op57n05  |     169|   230|2.1.1   |Adrian Nagel                             |Adrian Nagel|
|op57n06  |      95|   156|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op62n01  |      90|    72|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op62n02  |      81|   163|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op62n03  |      65|    95|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op62n04  |      81|    97|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op62n05  |      62|    45|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op62n06  |     150|   173|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op65n01  |     173|   203|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op65n02  |      26|   128|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op65n03  |      58|    87|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op65n04  |      71|   112|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op65n05  |      48|   128|2.1.1   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op65n06  |     179|   222|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op68n01  |      56|   156|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op68n02  |      88|   172|2.1.1   |Adrian Nagel                             |Adrian Nagel|
|op68n03  |     114|   134|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op68n04  |      90|    85|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op68n05  |      43|   103|2.1.1   |Adrian Nagel                             |Adrian Nagel|
|op68n06  |     202|   190|2.1.1   |Adrian Nagel                             |Adrian Nagel|
|op71n01  |      95|   175|2.1.1   |Adrian Nagel                             |Adrian Nagel|
|op71n02  |      54|   107|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op71n03  |      79|    72|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op71n04  |      77|    87|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op71n05  |      98|   155|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op71n06  |      32|   131|2.1.1   |Adrian Nagel                             |Adrian Nagel|
|op71n07  |      74|    74|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
