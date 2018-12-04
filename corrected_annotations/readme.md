Diese Annotationen wurden am 23.11. mit dem hier beiliegenden Julia-Programm update_syntax_0.5.1.jl aus den ursprünglichen, vom Annotator erstellten Textdateien erzeugt. Das Programm greift auf das ebenfalls enthaltene spelled_pitch0.5.jl zurück.

**Things that had to be corrected systematically:**

* insert key of the piece into the first symbol
* correct all key changes from absolute (e.g. `G. I` with space) to relative (e.g. `V.I`)
* correct all organ points:
  * instead of `I[I` annotator writes `"I`
  * instead of `I]` annotator writes `I"`
  * instead of `I[V` annotator writes `"I V`
  * if organ point ends on other than corresponding harmony, annotator writes `I V"` instead of `I]`
* correct `none` to `@none`
* change the symbol for every comment from `#` to `?`
* change the `X @alt Y` notation to `X-Y`
