// Example Vertex Shader

uniform ivec3 ViewportChanIndicies;
uniform float selectionPulse;
uniform int maskPreviewIndex;

uniform samplerBuffer Misc;
uniform samplerBuffer SurfaceIndicies;
uniform samplerBuffer Proj_Params;
uniform samplerBuffer realtimeData;
uniform samplerBuffer PixframeControl;
ivec2 	PixelCoords2D;

uniform sampler2D item0;
uniform sampler2D item1;
uniform sampler2D item2;
uniform sampler2D item3;
uniform sampler2D item4;
uniform sampler2D item5;
uniform sampler2D item6;
uniform sampler2D item7;
uniform sampler2D item8;
uniform sampler2D item9;
uniform sampler2D item10;
uniform sampler2D item11;
uniform sampler2D item12;
uniform sampler2D item13;
uniform sampler2D item14;
uniform sampler2D item15;

uniform sampler2DArray MASKS;
uniform sampler2DArray PIXFRAMES;

#define ProjTex0 item0
#define ProjTex1 item1
#define ProjTex2 item2
#define ProjTex3 item3
#define ProjTex4 item4
#define ProjTex5 item5
#define ProjTex6 item6
#define ProjTex7 item7
#define ProjTex8 item8
#define ProjTex9 item9
#define ProjTex10 item10
#define ProjTex11 item11
#define ProjTex12 item12
#define ProjTex13 item13
#define ProjTex14 item14
#define ProjTex15 item15

uniform int ProjectorBufferSize;
uniform int NumPasses;

#include <GLSL_SamplerFunctions>

/*
struct ProjectorObject
{
	mat4 	vm;
	mat4 	pm;

	float 	Pscale;
	int 	Pstyle;
	int 	Pextend;

	int 	Routingr;
	int 	Routingg;
	int 	Routingb;
	int 	Routinga;

	int 	Maskmode;

	// bool 	Coloroverride;

	float 	Setcolorr;
	float 	Setcolorg;
	float 	Setcolorb;
	float 	Setcolora;

	bool 	Projectoractive;

	float 	Gamma;
	float 	Gain;
	float 	Uvfxorigin;
	float 	Uvfxshuffle;
	int 	Projectorblendmode;
	int 	Projectorlayer;
};

ProjectorObject GetProjector( int projectorIndex ){
	
	// This function given a projector index, will assemble the data into a Projector struct, and return it.
	
	ProjectorObject Proj;

	int ProjectorStartingOffset = projectorIndex * ProjectorBufferSize;
	Proj.vm = mat4(0);
	Proj.pm = mat4(0);
	int row=0; int col=0;
	for( int i=0; i<16; i++ )
	{
		col = i % 4;
		row = i / 4;
		Proj.vm[row][col] = texelFetch(Proj_Params, ProjectorStartingOffset+i).x;
		
		col = i % 4;
		row = i / 4;
		Proj.pm[row][col] = texelFetch(Proj_Params, ProjectorStartingOffset+i+16).x;
	}

	Proj.Pscale = texelFetch(Proj_Params, ProjectorStartingOffset+32).x;
	Proj.Pstyle = int(texelFetch(Proj_Params, ProjectorStartingOffset+33).x);
	Proj.Pextend = int(texelFetch(Proj_Params, ProjectorStartingOffset+34).x);

	Proj.Routingr = int(texelFetch(Proj_Params, ProjectorStartingOffset+35).x);
	Proj.Routingg = int(texelFetch(Proj_Params, ProjectorStartingOffset+36).x);
	Proj.Routingb = int(texelFetch(Proj_Params, ProjectorStartingOffset+37).x);
	Proj.Routinga = int(texelFetch(Proj_Params, ProjectorStartingOffset+38).x);

	Proj.Maskmode = int(texelFetch(Proj_Params, ProjectorStartingOffset+39).x);

	// Proj.Coloroverride = bool(texelFetch(Proj_Params, ProjectorStartingOffset+40).x);

	Proj.Setcolorr = texelFetch(Proj_Params, ProjectorStartingOffset+41).x;
	Proj.Setcolorg = texelFetch(Proj_Params, ProjectorStartingOffset+42).x;
	Proj.Setcolorb = texelFetch(Proj_Params, ProjectorStartingOffset+43).x;
	Proj.Setcolora = texelFetch(Proj_Params, ProjectorStartingOffset+44).x;

	Proj.Projectoractive = bool(texelFetch(Proj_Params, ProjectorStartingOffset+45).x);

	Proj.Gamma = texelFetch(Proj_Params, ProjectorStartingOffset+46).x;
	Proj.Gain = texelFetch(Proj_Params, ProjectorStartingOffset+47).x;
	// Proj.Uvfxorigin = texelFetch(Proj_Params, ProjectorStartingOffset+48).x;
	// Proj.Uvfxshuffle = texelFetch(Proj_Params, ProjectorStartingOffset+49).x;
	Proj.Projectorblendmode = int(texelFetch(Proj_Params, ProjectorStartingOffset+50).x);

	// we may not need this in shader, since we are sorting our projectors in TD.
	Proj.Projectorlayer = int(texelFetch(Proj_Params, ProjectorStartingOffset+51).x);


	return Proj;
} 
*/


/*
vec4 WorldSpace_to_ProjectorSpace( vec4 WorldSpaceCoords , float CoordIndex , ProjectorObject pObj ){

	float PreMask = 1;

	// xform WS coordinates to projector space.
	pObj.vm 				= inverse(pObj.vm);
	vec4 Coords_VS 			= pObj.vm * WorldSpaceCoords;
	vec4 Coords_PS 			= pObj.pm * Coords_VS;
	
	// test if z coordinate is in front of camera or not - must do before perspective divide! it makes everything +
	float inFrontOfCamera = float(Coords_PS.z > -1);

	if(pObj.Pstyle == 0){ // if perspective mode!
		Coords_PS.xyz /= Coords_PS.w; // do perspective divide.
	}
	
	Coords_PS.xyz = Coords_PS.xyz * .5 + .5; // NDC to 0:1 space

	// if projector style is chase projector:
	if(pObj.Pstyle == 2){

		// go ahead and mask to extents of projection cube no matter what extend mode.
		PreMask = min( isInRange( Coords_PS.x , 0 , 1 ) , PreMask);
		PreMask = min( isInRange( Coords_PS.y , 0 , 1 ) , PreMask);
		
		// now that we have thee mask based on real coords, lets modify coords for 1d chase.
		// we use a map function and Pscale, any coords that still fall outside of 0:1 will be 
		// treated the same as other projector modes, via extend, cycle, mirror, etc.
		Coords_PS.x = map( CoordIndex , 0 , pObj.Pscale , 0 , 1 );
		Coords_PS.y = 0.5;
		Coords_PS.z = 0.5;
	}

	// breaking the rules a bit, storing the in front / behind mask in W since we won't use it again.
	Coords_PS.w = inFrontOfCamera * PreMask;

	return Coords_PS;
}
*/

in int PointIndex;
in int index;

out Vertex
{
	// vec4 xyzw;
	vec3 rgbIndicies;
	vec4 coords[16];
	flat int surfIndex;
	flat bool Selected;
	// float DEBUG;
} oVert;

void main() 
{
	vec4 worldSpacePos = TDDeform(P);
	gl_Position = TDWorldToProj(worldSpacePos);

	vec4 miscFetched = texelFetch( Misc , PointIndex );
	float redIndex = miscFetched.x;
	float greenIndex = miscFetched.y;
	float blueIndex = miscFetched.z;
	bool Selected = bool(miscFetched.w);

	int surfaceIndex = int(texelFetch( SurfaceIndicies , PointIndex ).x);

	ProjectorObject pObj;
	for( int i=0; i<NumPasses; i++ )
	{
		int 	projectorIndex 		= int(texelFetch(realtimeData, i).z);

		// 	// get the projector object by index.
		pObj = GetProjector(projectorIndex);

		oVert.coords[i] = WorldSpace_to_ProjectorSpace( vec4(Cd.xyz,1) , 0 , pObj );
	}
	

	// oVert.xyzw = vec4(Cd.xyz,1);
	oVert.rgbIndicies.xyz = vec3( redIndex , greenIndex , blueIndex );
	oVert.surfIndex = surfaceIndex;
	oVert.Selected = Selected;
}


