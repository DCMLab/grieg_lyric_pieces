#using DigitalMusicology
@enum Lang English German French Italian
const all_diatonics = Vector([1,2,3,4,5,6,7])
const diatonics_english = Dict(
    1 => "C",
    2 => "D",
    3 => "E",
    4 => "F",
    5 => "G",
    6 => "A",
    7 => "B",
    "C" => 1,
    "D" => 2,
    "E" => 3,
    "F" => 4,
    "G" => 5,
    "A" => 6,
    "B" => 7,
    "H" => 7)
const roman_majuscules = Dict(
    1 => "I",
    2 => "II",
    3 => "III",
    4 => "IV",
    5 => "V",
    6 => "VI",
    7 => "VII")
const roman_minuscules = Dict(
    1 => "i",
    2 => "ii",
    3 => "iii",
    4 => "iv",
    5 => "v",
    6 => "vi",
    7 => "vii")
const diatonics2pc = Dict(
    1 => 0,
    2 => 2,
    3 => 4,
    4 => 5,
    5 => 7,
    6 => 9,
    7 => 11)
const all_accidentals = Array([
    [0,0,0,0,0,0,0],    # C/a
    [0,0,1,0,0,0,1],    # D/b
    [0,1,1,0,0,1,1],    # E/c#
    [0,0,0,-1,0,0,0],   # F/d
    [0,0,0,0,0,0,1],    # G/e
    [0,0,1,0,0,1,1],    # A/f#
    [0,1,1,0,1,1,1]])   # B/g#
const translate_accidental = Dict(
    -6 => "bbbbbb",
    -5 => "bbbbb",
    -4 => "bbbb",
    -3 => "bbb",
    -2 => "bb",
    -1 => "b",
    0 => "",
    1 => "#",
    2 => "##",
    3 => "###",
    4 => "####",
    5 => "#####",
    6 => "######",
    "###" => 3,
    "##" => 2,
    "#" => 1,
    "" => 0,
    "b" => -1,
    "bb" => -2)

const pc2SP = Dict(
    0 => (1,0),
    1 => (2,-1),
    2 => (2,0),
    3 => (3,-1),
    4 => (3,0),
    5 => (4,0),
    6 => (5,-1),
    7 => (5,0),
    8 => (6,-1),
    9 => (6,0),
    10 => (7,-1),
    11 => (7,0))

struct pc # <: Pitch
    int :: Int64
end

Base.Int(pc::pc) = pc.int

Base.show(io::IO, pitch::pc) = print(io,pitch.int)

Base.:+(p1::pc,p2::pc) = p1.int+p2.int

struct SP #<: Pitch
    pitch :: Tuple{Int64,Int64}
    english :: String
    pc :: pc

    SP(t::Tuple{Int64,Int64}) = new(t,SP2english(t),tuple2PC(t))
    function SP(str::AbstractString,::Val{English})
        let t = english2SP(str)
            new(t,str,tuple2PC(t))
        end
    end

end

function SP2english(t::Tuple{Int64,Int64})
    d,a = t
    diatonics_english[d]*translate_accidental[a]
end

function english2SP(str::AbstractString)
    let d = diatonics_english[uppercase(str[1:1])]
        length(str) > 1 ? (d,translate_accidental[str[2:end]]) : (d,0)
    end
end

format_eng(str::AbstractString) = length(str) > 1 ? uppercase(str[1:1])*lowercase(str[2:end]) : uppercase(str[1:1])

SP(str::AbstractString) = SP(str,Val{English}())
SP(i::Int64) = SP(pc2SP[i])
SP(pc::pc) = SP(pc.int)
tuple2PC(t::Tuple{Int64,Int64}) = pc(mod(diatonics2pc[t[1]]+t[2],12))

function distance(p1::Int64,p2::Int64)
    if abs(p2-p1)>6
        p2>p1 ? p2-p1-12 : p2+12-p1
    else
        p2-p1
    end
end

distance(p1::pc,p2::pc) = distance(p1.int,p2.int)

function transposeby(sp::SP,interval::SP)
    ord,ora = sp.pitch
    opc = sp.pc.int
    ivd,iva = interval.pitch
    ipc = interval.pc.int
    tpc = mod(opc+ipc,12)
    ttd = mod((ord-1)+(ivd-1),7)+1
    intermediary_pc = tuple2PC((ttd,ora)).int
    tta = ora + distance(intermediary_pc,tpc)
    SP((ttd,tta))
end


transposeby(sp::SP,i::Int64) = transposeby(sp,SP(pc2SP[i]))
transposeby(sp::SP,pc::pc) = transposeby(sp,pc.int)
transposeby(sp::SP,str::AbstractString) = transposeby(sp,SP(str))
transposeby(sp::SP,t::Tuple{Int64,Int64}) = transposeby(sp,SP(t))
transposeby(str::AbstractString,b) = transposeby(SP(str),b)

SP(spv::Vector{Tuple{Int64,Int64}}) = map(SP,spv)

transposeby(SP(diatonics_english[6]),SP(3))

abstract type Scales #<: PitchCollections
end


mutable struct Major <: Scales

    diatonic :: Vector{Int64}
    accidentals :: Vector{Int64}
    pitches :: Vector{SP}
    pcs :: Vector{pc}

    function Major(d::Int64=1) # 1=C, 7=B
        dia = circshift(all_diatonics,-d+1)
        acc = all_accidentals[d]
        sps = SP(collect(zip(dia,acc)))
        pcs = map(x -> getfield(x,:pc),sps)
        new(dia,acc,sps,pcs)
    end
    function Major(t::Tuple{Int64,Int64})
        d,a = t
        stranspose!(Major(d),a)
    end
end



#function Base.getproperty(s::Scales,::Val{:pcs})
#    neu = map(x -> getfield(x,:pc),s.pitches)
#    Core.setfield!(s, :pcs, neu)
#    println("Ja")
#    neu
#end

function update_pitches!(s::Scales)
     dia = s.diatonic
     acc = s.accidentals
     sps = SP(collect(zip(dia,acc)))
     pcs = map(x -> getfield(x,:pc),sps)
     Core.setfield!(s, :pitches, sps)
     Core.setfield!(s, :pcs, pcs)
     s
end

function Base.setproperty!(m::Scales,name::Symbol,neu::Vector{Int64})
    Core.setfield!(m, name, neu)
####Änderungern einfügen, wenn eine Eigenschaft neu zugewiesen wird
    #name == :accidentals && update_pitches!(m)
end

function stranspose!(s::Scales,semitones::Int64)
    s.accidentals += semitones * ones(Int64,7)
    update_pitches!(s)
end

stranspose(s::Scales,sp::SP) = stranspose(s,sp.pitch)

Base.in(pc::Int64,s::Scales) = findfirst(x -> x.int == pc,s.pcs)
function Base.in(sp::SP,s::Scales,c::AbstractChar=' ')
    d,a=sp.pitch
    d_pos = findfirst(x -> d == x.pitch[1],s.pitches)
    if sp.pc != s.pcs[d_pos]
        ret = (d_pos,distance(s.pcs[d_pos],sp.pc))
    else
        ret = (d_pos,0)
    end
    if c != ' '
        if islowercase(c)
            ret = translate_accidental[ret[2]] * roman_minuscules[ret[1]]
        else
            ret = translate_accidental[ret[2]] * roman_majuscules[ret[1]]
        end
    end
    ret
end

Base.in(str::AbstractString,s::Scales) = in(SP(str),s,str[1])

#in("f#",Major("c"))

function stranspose(s::Major,target=Tuple{Int64,Int64})
    Major(target)
end


Major(str::AbstractString) = Major(SP(str))
Base.circshift(s::Scales,i::Int64) = map(x -> vec(circshift(x,i)),(s.diatonic,s.accidentals,s.pitches,s.pcs))



mutable struct Minor <: Scales

    diatonic :: Vector{Int64}
    accidentals :: Vector{Int64}
    pitches :: Vector{SP}
    pcs :: Vector{pc}

    function Minor(d::Int64=1)
        relative = transposeby(SP(diatonics_english[d]),SP(3))
        relative_scale = Major(relative)
        d,a,ps,pcs=circshift(relative_scale,2)
        new(d,a,ps,pcs)
    end
    function Minor(t::Tuple{Int64,Int64})
        d,a = t
        stranspose!(Minor(d),a)
    end
end

function stranspose(s::Minor,target=Tuple{Int64,Int64})
    Minor(target)
end

Major(pitch::pc) = Major(pc2SP[pitch.int])
Major(s::SP) = Major(s.pitch)
Minor(str::AbstractString) = Minor(SP(str))
Minor(pitch::pc) = Minor(pc2SP[pitch.int])
Minor(s::SP) = Minor(s.pitch)

scale(str::AbstractString) = isuppercase(str[1]) ? Major(SP(str).pitch) : Minor(SP(str).pitch)

scale(sp::SP) = scale(sp.english)

function Base.getindex(s::Scales,i::Int64)
    s.pitches[i]
end
