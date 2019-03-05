cd("/e/Documents/DCML/Grieg/korrigierte Annotations/")
#cd(@__DIR__)
include("spelled_pitch0.5.jl")
using DelimitedFiles, Dates

@enum Cases Idle StartPP EndPP Ambiguous Comment Localkey Error Five

const regex = r"""^
    (\.)?
    ((?P<key>[a-gA-G](b*|\#*)|(b*|\#*)(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i))\.)?
    ((?P<pedal>(b*|\#*)(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i))\[)?
    (?P<numeral>(b*|\#*)(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i|Ger|It|Fr))
    (?P<form>[%o+M])?
    (?P<figbass>(9|7|65|43|42|2|64|6))?
    (\((?P<changes>(\+?(b*|\#*)\d)+)\))?
    (/\.?(?P<relativeroot>(b*|\#*)(VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i)))?
    (?P<pedalend>\])?
    (?P<phraseend>\\\\)?$
    """x

function update(s::Array{String},::Val{Idle})
    prod(s)
end


function update(s::Array{String},::Val{StartPP})
    beginning = s[1]
    numeral = match(r"\"([b*|\#*]*[VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i])",beginning)[1]
    if length(s) > 1
        return numeral * "[" *s[2]
    else
        replace(beginning,"\"" => numeral * "[")
    end
end

function update(s::Array{String},::Val{EndPP})
    if length(s) == 1
        replace(s[1], "\"" => "]")
    else
        s[1]*"]"
    end
end


function update(s::Array{String},::Val{Ambiguous})
    pos = findall(s .== "@alt")[1]
    a = s[1:pos-1]
    a = update(a,Val{choosecase(a)}())
    b = s[pos+1:end]
    b = update(b,Val{choosecase(b)}())
    "$a-$b"
end

function update(s::Array{String},::Val{Comment})
    symbol = findfirst(isequal("#"),s)
    com = "? "*join(s[symbol+1:end]," ")
    Str = join(s[1:symbol-1],"\t")
    update(Str,com)
end

function update(s::Array{String},::Val{Five})
    for p in findall(x -> occursin(r"[VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i]5",x),s)
        s[p] = replace(s[p],r"([VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i])5" => s"\1")
    end
    update(s,Val{choosecase(s)}())
end

function update(s::Array{String},::Val{Localkey})
    k, harmony = s
    k = k[1:length(k)-1]
    global Key
    numeral = in(k,scale(Key))
    h = String.(split(harmony))
    numeral*"."*update(h,Val{choosecase(h)}())
end


function update(s::Array{String},::Val{Error})
    "ERROR"
end

@doc """
    choosecase()

sghhg
""" ->
function choosecase(s::Array{String})
    if length(s)>1
        in("#",s) && return Comment
        s[2] == "@alt" && return Ambiguous
    end

    if length(findall(x -> occursin(r"[VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i]5",x),s)) > 0 return Five end

    if s[1][1] == '\"'
        return StartPP
    elseif any(map(x -> occursin(r"\S\"",x),s))
        return EndPP
    elseif length(s)>1
        Localkey
    else
        Idle
    end
end



function update(s::AbstractString,comment::AbstractString)
    h = String.(split(s))
    update(h,Val{choosecase(h)}()) * " $comment"
end

function incorrectsyntax(s::AbstractString)
    h = String.(split(s))[1]
    for i in String.(split(h,'-'))
        if !occursin(regex,i)
            return true
        end
    end
    false
end

function update(a::Array{SubString{String}})
    m, b, h = String(a[1][2:end]), String(a[2]), String.(a[3:end])
    let pos = findfirst(isequal("none"),h)
        pos != nothing ? h[pos] = "@none" : nothing
    end
    case = choosecase(h)
    #println(h,case)
    correct = update(h,Val{case}())
    if case != Idle
        lo = "$m $b $(join(h,' ')) => $correct"
        if incorrectsyntax(correct) lo = lo * "\n!!!!!!!!!!!!!!!!!!!! $(split(correct)[1]) syntactically incorrect !!!!!!!!!!!!!!!!!!!!" end
        global meta
        push!(meta,lo)
        println(lo)
    end
    m, b, correct
end

function update(filename::AbstractString, skip_rows::Int=0)
    lines = open(readlines, filename)
    info = splice!(lines,1:skip_rows)
    info = info[map(x -> "" != x,info)] #strip empty lines

    d = map(x -> String.(x), split.(info))
    d = Dict(d[i][1] => d[i][2] for i in 1:length(d))
    global Key = d["@key:"]
    global meta = [Dates.format(now(),"dd.mm.yyyy HH:MM: ") * "update_syntax_0.5.1.jl\nCORRECTIONS\n___________"]
    splitlines = split.(lines)
    info = append!(["@skip: " * string(length(info)+1)],info)
    println("Updating $filename, standing in $Key")
    new = update.(splitlines)
    frst = (new[1][1], new[1][2], ".$Key." * new[1][3])
    new[1] = frst
    #new[1][3] = ".$Key." * new[1][3] did not work
    new, meta, info
end

function doit(oldfile::AbstractString,suffix::AbstractString="_new",folder="")
    name, extension = match(r"(.*)(\.[A-Za-z0-9]+$)",oldfile).captures
    target = folder * name * suffix
    new,log,info = update(oldfile,5)
    writedlm(target*extension,info,quotes=false)
    io = open(target*extension,"a")
    writedlm(io,new,quotes=false)
    close(io)
    writedlm(target*".log",log,quotes=false)
end


function dofolder(path::AbstractString)
    cd(path)
    files = filter(x -> !occursin("_new",x) && occursin("op",x), readdir(path))
    for f in files
        #println(f)
        doit(f,"","../korrigierte Annotations/")
    end
end

#doit("op12n01.txt")

dofolder("/e/Documents/DCML/Grieg/Annotations")
#Base.print_matrix(stdout,updatedlines[1:5])
